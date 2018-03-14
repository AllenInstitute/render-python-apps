import renderapi
import os
import sys
from ..module.render_module import RenderModule, RenderParameters
import argschema
import numpy as np
import FibicsAtlasImport_1_1 as FibicsAtlasImport

example_json={
        "render":{
            'host':'ibs-forrestc-ux1',
            'port':8080,
            'owner':'Forrest',
            'project':'M247514_Rorb_1',
            'client_scripts':'/pipeline/render/render-ws-java-client/src/main/scripts'
        },
        "stack":"BIGALIGN_LENS_DAPI_1_deconvnew",
        "roi":[[165000,-126000],[176000,-126000],[176000,-115000],[165000,-115000]],
        "zrange":[0,49],
        "xml_file":"C:\\Users\\olgag\\Documents\\ATLASimport\\M247514_Rorb_1_roi.a5import"
}

class CreateFibicsXMLParameters(RenderParameters):
    stack = argschema.fields.Str(required=True,
        description='render stack to get roi from')
    xml_file = argschema.fields.OutputFile(required=True,
        description='path to same fibics xml file')
    roi = argschema.fields.NumpyArray(dtype=np.float,
        description='Nx2 (x,y) array of roi points, not closed')
    zrange = argschema.fields.List(argschema.fields.Int,required=True,
        description='range of z values to include in output min,max')

sx = 0.1013 #scaleX from metadata
sy = 0.1013 #scaleY from metadata
def local_to_stage_coord(r,stack,x,y,tileId):
    ts = r.run(renderapi.tilespec.get_tile_spec,stack,tileId)
    x_stage = (x - (ts.width - 1)/2)*sx + ts.layout.stageX
    y_stage = (y - (ts.height - 1)/2)*sy + ts.layout.stageY
    return x_stage, y_stage

def roi_to_stage_coord_3d(r,stack,zrange,roi):
    zvalues =r.run(renderapi.stack.get_z_values_for_stack,stack)
    roi_stage_list = []
    for z in zvalues[zrange[0]:zrange[1]+1]:
        roi_stage = np.zeros(roi.shape)
        for i in range(roi.shape[0]):
            x,y = roi[i,:]
            coord_list = r.run(renderapi.coordinate.world_to_local_coordinates,stack,z,x,y)
            x_local, y_local = coord_list[-1]['local'][0:2]
            tileId = str(coord_list[-1]['tileId'])
            roi_stage[i,:] = local_to_stage_coord(r,stack,x_local,y_local,tileId)
        roi_stage_list.append(roi_stage)
    return roi_stage_list

class SimpleTransform():
    def __init__(self,scale=1.0,rotation=0.0,xoffset=0.0,yoffset=0.0,cx=0.5,cy=0.5):
        self.ptform = FibicsAtlasImport.ParentTransform()
        self.ptform = FibicsAtlasImport.ParentTransform()
        self.ptform.M11 = scale*np.cos(rotation)
        self.ptform.M12 = scale*np.sin(rotation)
        self.ptform.M13 = 0.0
        self.ptform.M14 = 0.0
        self.ptform.M21 = scale*np.sin(rotation)
        self.ptform.M22 = scale*np.cos(rotation)
        self.ptform.M23 = 0.0
        self.ptform.M24 = 0.0
        self.ptform.M31 = 0.0
        self.ptform.M32 = 0.0
        self.ptform.M33 = 1.0
        self.ptform.M34 = 0.0
        self.ptform.M41 = xoffset
        self.ptform.M42 = yoffset
        self.ptform.M43 = 0.0
        self.ptform.M44 = 1.0
        self.ptform.CenterLocalX = cx
        self.ptform.CenterLocalY = cy

def create_PrecisionSiteSpec(fa,name,roi_list): #same Overview and HighRes, use to import sections
    for i, roi in enumerate(roi_list):    
            pss = FibicsAtlasImport.PrecisionSiteSpec()
            pss.Name = name + str(i)
            pss.SaveLocation = 'C:/Temp/'
            tform = SimpleTransform(cx=0.0,cy=0.0)
            pss.ParentTransform = tform.ptform 
            
            prot_name1 = 'Live Imaging'
            pss.Overview = prot_name1
            prot_name2 = 'Live Imaging'
            pss.HighRes = prot_name2
            ge = FibicsAtlasImport.Geometry()
            ge.Type = 'Polygon'
            for i in range(roi.shape[0]):
                ve = FibicsAtlasImport.Vertex()
                ve.X, ve.Y = roi[i,:] 
                ge.Vertex.append(ve)
            pss.Overview.Geometry = ge    
            pss.HighRes.Geometry = ge
            
            fa.PrecisionSiteSpec.append(pss)
            
    return fa.PrecisionSiteSpec
        
class CreateFibicsXML(RenderModule):
    default_schema = CreateFibicsXMLParameters
    
    def run(self):
        self.logger.error('WARNING NEEDS TO BE TESTED, TALK TO FORREST IF BROKEN')
        
        roi_stage_list = roi_to_stage_coord_3d(self.render,self.args['stack'],self.args['zrange'],self.args['roi'])
       
        fa = FibicsAtlasImport.FibicsAtlas5Import()
        fa.version = 1.1 
        fa.PrecisionSiteSpec = create_PrecisionSiteSpec(fa,'Section', roi_stage_list)
        
        out = open(self.args['xml_file'],'w')
        out.write(fa.toxml())
        out.close() 

if __name__ == "__main__":
    mod = CreateFibicsXML(input_data= example_json)
    mod.run()



