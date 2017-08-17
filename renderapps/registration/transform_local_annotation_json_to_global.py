import renderapi
import json
import os
from ..module.render_module import RenderTrakEM2Parameters, RenderModule
from ..TrakEM2.AnnotationJsonSchema import AnnotationJsonSchema
from ..shapely import tilespec_to_bounding_box_polygon
from argschema.fields import Str, InputFile
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
    "trakem2project":"/nas4/data/EM_annotation/annotationFilesForJHU/annotationTrakEMprojects_M247514_Rorb_1/m247514_Site3Annotation_RD.xml",
    "outputAnnotationFile":"/nas4/data/EM_annotation/annotationFilesForJHU/m247514_Site3Annotation_RD.json",
    "renderHome":"/pipeline/render"
}


class TransformLocalAnnotationParameters(RenderTrakEM2Parameters):
    stack = Str(required=True,description='stack to look for transform annotations into')
    input_annotation_file = InputFile(required=True,description='path to annotation file')
    output_annotation_file = Str(required=True,description='path to save transformed annotation')


def transform_annotations(render,stack,local_annotation):
    """ transforms a dictionary of local_annotations i.e. from ImportTrakEM2Annotations
    into a global coordinate system specified by stack.

    Parameters
    ----------
    render: renderapi.client.RenderClient
        render connect object to a render server
    stack: str
        a string specifying the render stack to find the tileIds and transform the coordinates
    local_annotation: dict
        a local annotation dictionary that conforms to the AnnotationJonsSchema.AnnotationFile schema
        with coordinates expressed in local coordinates
    
    Returns:
    dict
        a global annotation dictionary that conforms to the AnnotationJsonSchema.AnnotationFile schema
        with coordinates expressed in global coordinates
    """

    #loop over annotations
    for area_list in local_annotation['area_lists']:
        for area in area_list['areas']:
            for path in area['paths']:
                for tile_path in area['tile_paths']:
                    tile_path['path']=renderapi.coordinate.local_to_world_coordinates_array(
                        stack,tile_path['path'],tile_path['z'],doClientSide=True,render=render)
                        

class TransformLocalAnnotation(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = TransformLocalAnnotationParameters
        super(TransformLocalAnnotation,self).__init__(schema_type=schema_type,*args,**kwargs)
    def run(self):

        self.logger.error('WARNING NEEDS TO BE TESTED, TALK TO FORREST IF BROKEN')

        with open(self.args['input_annotation_file'],'r') as fp:
            local_annotation_json = json.load(fp)
            schema = AnnotationFile()
            local_annotation = schema.load(local_annotation_json)
        #read in the json file
        transform_annotations(self.render,
                              self.args['stack'],
                              local_annotation)


if __name__ == "__main__":
    mod = TransformLocalAnnotation(input_data= parameters)
    mod.run()
