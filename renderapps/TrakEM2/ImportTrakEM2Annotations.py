import numpy as np
import renderapi
import json
import os
from ..module.render_module import RenderTrakEM2Parameters, TrakEM2RenderModule
from ..shapely import tilespec_to_bounding_box_polygon
from argschema.fields import Str, InputFile, OutputFile
from shapely import geometry
import lxml.etree
from AnnotationJsonSchema import AnnotationFile

parameters={
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":8080,
        "owner":"Forrest",
        "project":"M247514_Rorb_1",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    "EMstack":"ALIGNEM_reg2",
    "trakem2project":"/nas4/data/EM_annotation/annotationFilesForJHU/annotationTrakEMprojects_M247514_Rorb_1/m247514_Site3Annotation_cropedToMatch_MN.xml",
    "outputAnnotationFile":"/nas4/data/EM_annotation/annotationFilesForJHU/m247514_Site3Annotation_cropedToMatch_MN_local.json",
    "renderHome":"/pipeline/render"
}



parameters={
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":8080,
        "owner":"Forrest",
        "project":"M247514_Rorb_1",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    "EMstack":"ALIGNEM_reg2",
    "trakem2project":"/nas4/data/EM_annotation/annotationFilesForJHU/annotationTrakEMprojects_M247514_Rorb_1/m247514_Site3Annotation_cropedToMatch_SD.xml",
    "outputAnnotationFile":"/nas4/data/EM_annotation/annotationFilesForJHU/m247514_Site3Annotation_cropedToMatch_SD_local.json",
    "renderHome":"/pipeline/render"
}

parameters={
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":8080,
        "owner":"Forrest",
        "project":"M247514_Rorb_1",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    "EMstack":"ALIGNEM_reg2",
    "trakem2project":"/nas4/data/EM_annotation/annotationFilesForJHU/annotationTrakEMprojects_M247514_Rorb_1/m247514_Site3Annotation_RD.xml",
    "outputAnnotationFile":"/nas4/data/EM_annotation/annotationFilesForJHU/m247514_Site3Annotation_RD_local.json",
    "renderHome":"/pipeline/render"
}

class AnnotationConversionError(Exception):
    pass

class ImportTrakEM2AnnotationParameters(RenderTrakEM2Parameters):
    EMstack = Str(required=True,description='stack to look for trakem2 patches in')
    trakem2project = InputFile(required=True,description='trakem2 file to read in')
    output_json = OutputFile(required=True,description="place to save annotation output")

def convert_path(path,tform):
    #function to convert TEM2 path using the transformation tform
    #convert_path(path,tform):
    d = path.attrib['d'].split(' ')
    Nelem = int(np.ceil(len(d)*1.0/3))
    points = np.zeros((Nelem,2))

    for k,i in enumerate(range(0,len(d)+1,3)):

        if d[i]=='M':
            points[k,:]=[float(d[i+1]),float(d[i+2])]
        elif d[i]=='L':
            points[k,:]=[float(d[i+1]),float(d[i+2])]
        elif d[i]=='z':
            points[k,:]=points[0,:]
    return tform.tform(points)

def convert_transform(tfs):
    tfs=tfs.replace('matrix(','')
    tfs=tfs.replace(')','')
    vals = tfs.split(',')
    tform = renderapi.transform.AffineModel(M00 = vals[0],
                                           M10 = vals[1],
                                           M01 = vals[2],
                                           M11 = vals[3],
                                           B0  = vals[4],
                                           B1  = vals[5])
    return tform

def form_area(path_numpy,ts,rts):
    tile_path_d={}

    local_path = path_numpy
    tmp=list(ts.tforms)
    tmp.reverse()
    for t in tmp:
        local_path = t.inverse_tform(local_path)
    tile_path_d['tileId']=rts.tileId
    #tile_path_d['z']=rts.z
    #print 'z',rts.z,layerid,al.attrib['oid']
    tile_path_d['local_path']=local_path
    return tile_path_d
def form_areas(shape,ts,rts,area_list_d):
    if isinstance(shape,geometry.MultiPolygon):
        for s in shape:
            path_numpy = np.asarray(s.exterior)
            tile_path_d = form_area(path_numpy,ts,rts)
            area_list_d['areas'].append(tile_path_d)
    elif isinstance(shape,geometry.Polygon):
        path_numpy = np.asarray(shape.exterior)
        tile_path_d = form_area(path_numpy,ts,rts)
        area_list_d['areas'].append(tile_path_d)
    else:
        raise AnnotationConversionError("unknown shape type {}".format(type(shape)))

def parse_area_lists(render_tilespecs,tem2_tilespecs,tem2_polygons,root,area_lists):
    json_output = {'area_lists':[]}
    for thisid,al in enumerate(area_lists):
        areas = al.findall('t2_area')
        links=al.attrib['links']
        tform = convert_transform(al.attrib['transform'])
        area_list_d = {}
        area_list_d['oid']=al.attrib['oid']
        area_list_d['id']=thisid
        area_list_d['areas']=[]
        for area in areas:

            layerid=area.attrib['layer_id']    

            layer=root.find('//t2_layer[@oid="%s"]'%layerid)
            patches = [patch for patch in layer.getchildren()]
            patchids = [patch.attrib['oid'] for patch in patches]
            layer_tilespecs = [(poly,ts,t) for poly,ts,t in zip(tem2_polygons,tem2_tilespecs,render_tilespecs) if ts.tileId in patchids]
            #reverse the tilespecs so they are encountered from top to bottom when iterated over
            layer_tilespecs.reverse()
            paths = area.findall('t2_path')
            #loop over all the paths
            for path in paths:
                #initialize the path's polygon with the entire path
                path_numpy= convert_path(path,tform)
                path_poly = geometry.Polygon(path_numpy)
                for poly,ts,rts in layer_tilespecs:
                   
                    if poly.contains(path_poly):
                        #then the remaining path_poly is completely contained
                        #on this tile, 
                        form_areas(path_poly,ts,rts,area_list_d)
                        #and we should be done writing down the annotation so break
                        break
                    if poly.intersects(path_poly):
                        #print 'partial',area_list_d['oid']
                        #then only a piece of the path is completely contained on this tile
                        #and we should cut out the part that is and write that down
                        on_tile_poly = path_poly.intersection(poly)

                        form_areas(on_tile_poly,ts,rts,area_list_d)
                        # and cut off the part that isn't overlapping
                        # and alter path_poly, leaving it to be handled by lower tiles
                        path_poly = path_poly.difference(poly)

        json_output['area_lists'].append(area_list_d)
    return json_output


class ImportTrakEM2Annotations(TrakEM2RenderModule):
    default_schema = ImportTrakEM2AnnotationParameters
    default_output_schema = AnnotationFile
    
    def run(self):
        print self.args
        tem2file = self.args['trakem2project']
        trakem2dir = os.path.split(tem2file)[0]
        jsonFileOut = os.path.join(trakem2dir,os.path.splitext(tem2file)[0]+'.json')

        #convert the trakem2 project to a json tilespec
        self.convert_trakem2_project(tem2file,trakem2dir,jsonFileOut)

        #read in the tilespecs from the json, and parse them with api
        tsjson = json.load(open(jsonFileOut,'r'))
        tem2_tilespecs = [renderapi.tilespec.TileSpec(json=tsj) for tsj in tsjson]

        #loop over the tem2 tilespecs to find the corresponding render tilespecs
        # matching based upon the filename (due to moving of the data)

        render_tilespecs = []
        for ts in tem2_tilespecs:
            pot_render_tilespecs = self.render.run(renderapi.tilespec.get_tile_specs_from_z,
                                                self.args['EMstack'],
                                                ts.z)
            filepath = (os.path.split(ts.ip.get(0)['imageUrl'])[1]).split('_flip')[0]
            pot_filepaths = [(os.path.split(t.ip.get(0)['imageUrl'])[1]).split('_flip')[0] for t in pot_render_tilespecs]
            render_tilespecs.append(next(t for t,fp in zip(pot_render_tilespecs,pot_filepaths) if fp==filepath))
        #convert the tem2_tilespecs to shapely polygons
        tem2_polygons = [tilespec_to_bounding_box_polygon(ts) for ts in tem2_tilespecs]

        #parse the TEM2 project
        root = lxml.etree.parse(open(tem2file,'r'))

        #get the area lists
        area_lists=root.findall('//t2_area_list')
        area_lists = [al for al in area_lists if (len(al.getchildren())>0)]
        print 'project contains %d area lists'%len(area_lists)

        #parse the area lists into json
        json_output = parse_area_lists(render_tilespecs,tem2_tilespecs,tem2_polygons,root,area_lists)

        #dump the json dictionary through the AnnotationFile schema
        #in order to serialize it to disk

        schema = AnnotationFile()
        self.output(json_output)

if __name__ == "__main__":
    mod = ImportTrakEM2Annotations(input_data= parameters)
    mod.run()
