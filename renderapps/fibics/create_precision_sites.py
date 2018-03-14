import renderapi
from ..module.render_module import RenderModule, RenderParameters
import argschema
import numpy as np
import FibicsAtlasImport_1_1 as FibicsAtlasImport

example_json={
        "render": {
            "host": "ibs-forrestc-ux1",
            "port": 8080,
            "owner": "S3_Run1",
            "project": "S3_Run1_Jarvis",
            "client_scripts": "/var/www/render/render-ws-java-client/src/main/scripts"
        },
        "stack": "Fine_Aligned_68_to_112_DAPI_1_fullscale_final",
        "roi": [8679, 22193, 296, 296],
        "zrange": [0, 15],
        "xml_file": "C:\\Users\\olgag\\Documents\\ATLASimport\\S3_Run1_Jarvis_Ribbon0068_pss.a5import"
}

class CreatePrecisionSitesParameters(RenderParameters):
    stack = argschema.fields.Str(required=True,
        description="render stack to get roi from")
    xml_file = argschema.fields.OutputFile(required=True,
        description="path to fibics xml file")
    roi = argschema.fields.List(argschema.fields.Int, required=True,
        description="rectangle with a center x0, y0, width dx, and height dy")
    zrange = argschema.fields.List(argschema.fields.Int, required=True,
        description="range of z values to include in output min, max")

def define_roi(roi): #rectangle with a center(x0,y0), width (dx) and height (dy)
    x0, y0, dx, dy = roi
    roi_center = np.array([[x0, y0]])
    roi_norms = np.array([[x0, y0 + dy/2], [x0 + dx/2, y0], [x0, y0 - dy/2],
                          [x0 - dx/2, y0]])
    return roi_center, roi_norms

sx = 0.103175 #scaleX from metadata
sy = 0.103175 #scaleY from metadata
def local_to_stage_coord(r, stack, x, y, tileId):
    ts = renderapi.tilespec.get_tile_spec(stack, tileId, render=r)
    x_stage = (x - (ts.width - 1)/2)*sx + ts.layout.stageX
    y_stage = (y - (ts.height - 1)/2)*sy + ts.layout.stageY
    return x_stage, y_stage

def roi_to_stage_coord_3d(r, stack, z_range, roi_center, roi_norms):
    zvalues = renderapi.stack.get_z_values_for_stack(stack, render=r)
    roi_center_stage_list = []
    roi_norms_stage_list = []
    for z in zvalues[z_range[0]:z_range[1] + 1]:
        roi_center_stage = np.zeros(roi_center.shape)
        x0, y0 = roi_center[0]
        center_coord_list = renderapi.coordinate.world_to_local_coordinates(
            stack, z, x0, y0, render=r)
        x0_local, y0_local = center_coord_list[-1]['local'][0:2]
        center_tileId = str(center_coord_list[-1]['tileId'])
        roi_center_stage[:] = local_to_stage_coord(r, stack, x0_local, 
                                                   y0_local, center_tileId)
        roi_center_stage_list.append(roi_center_stage)
        
        roi_norms_stage = np.zeros(roi_norms.shape)
        for i in range(roi_norms.shape[0]):
            xn, yn = roi_norms[i,:]
            norms_coord_list = renderapi.coordinate.world_to_local_coordinates(
                stack, z, xn, yn, render=r)
            xn_local, yn_local = norms_coord_list[-1]['local'][0:2]
            norms_tileId = str(norms_coord_list[-1]['tileId'])
            roi_norms_stage[i,:] = local_to_stage_coord(r, stack, xn_local,
                                                        yn_local, norms_tileId)
        roi_norms_stage_list.append(roi_norms_stage)
        
    return roi_center_stage_list, roi_norms_stage_list

def calculate_angle(roi_center, roi_norms): 
    vector = np.array([[0, -1], [-1, 0], [0, 1], [1, 0]]) 
    angle3 = np.zeros((roi_norms.shape[0], 1))
    for i in range(roi_norms.shape[0]):
        angle1 = np.arctan2(vector[i,1], vector[i,0])
        angle2 = np.arctan2(roi_norms[i, 1] - roi_center[0, 1],roi_norms[i, 0] 
                            - roi_center[0, 0])
        angle3[i] = angle2 - angle1 
    angle = np.mean(angle3)
    return angle        

def calculate_angles(roi_center_list, roi_norms_list):
    angle_list = []
    for i in range(len(roi_center_list)):
        angle = calculate_angle(roi_center_list[i], roi_norms_list[i])
        angle_list.append(angle) 
    return angle_list 
   
class Full2DTransform():
    def __init__(self, M11, M12 ,M21, M22 ,M41, M42, cx=0.5, cy=0.5):
        self.ptform = FibicsAtlasImport.ParentTransform()
        self.ptform = FibicsAtlasImport.ParentTransform()
        self.ptform.M11 = M11
        self.ptform.M12 = M12
        self.ptform.M13 = 0.0
        self.ptform.M14 = 0.0
        self.ptform.M21 = M21
        self.ptform.M22 = M22
        self.ptform.M23 = 0.0
        self.ptform.M24 = 0.0
        self.ptform.M31 = 0.0
        self.ptform.M32 = 0.0
        self.ptform.M33 = 1.0
        self.ptform.M34 = 0.0
        self.ptform.M41 = M41
        self.ptform.M42 = M42
        self.ptform.M43 = 0.0
        self.ptform.M44 = 1.0
        self.ptform.CenterLocalX = cx
        self.ptform.CenterLocalY = cy

def create_PrecisionSiteSpec(fa, name, roi_center_list, angle_list): #same Overview and HighRes, shift, rotation, flip
    for i, roi in enumerate(roi_center_list):    
            pss = FibicsAtlasImport.PrecisionSiteSpec()
            pss.Name = name + str(i)
            pss.SaveLocation = "C:\\Temp\\110617"
            angle = angle_list[i]
            tform = Full2DTransform(M11=np.cos(angle), M12=np.sin(angle), 
                                    M21=np.sin(angle), M22=-np.cos(angle), 
                                    M41=roi[0,0], M42=roi[0,1], cx=0.0, cy=0.0)
            
            pss.ParentTransform = tform.ptform 
            
            prot_name1 = "MN_InLens_30nm_4us_61umFOV Duplicate"
            pss.Overview = prot_name1
            prot_name2 = "MN_InLens_3nm_5us_15umFOV Duplicate"
            pss.HighRes = prot_name2
            
            fa.PrecisionSiteSpec.append(pss)
            
    return fa.PrecisionSiteSpec
        
class CreatePrecisionSites(RenderModule):
    default_schema = CreatePrecisionSitesParameters
    
    def run(self):
        self.logger.error('WARNING NEEDS TO BE TESTED, TALK TO FORREST IF BROKEN')
        
        roi_center, roi_norms = define_roi(self.args['roi'])
        roi_center_stage_list, roi_norms_stage_list = roi_to_stage_coord_3d(
                self.render, self.args['stack'], self.args['zrange'], 
                roi_center, roi_norms)
        angle_list = calculate_angles(roi_center_stage_list, roi_norms_stage_list)
        fa = FibicsAtlasImport.FibicsAtlas5Import()
        fa.version = 1.1 
        fa.PrecisionSiteSpec = create_PrecisionSiteSpec(fa, 'Sec', 
                                             roi_center_stage_list, angle_list)
        
        out = open(self.args['xml_file'], 'w')
        out.write(fa.toxml())
        out.close() 

if __name__ == "__main__":
    mod = CreatePrecisionSites(input_data= example_json)
    mod.run()


