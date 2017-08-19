import renderapi
import json
import os
from ..module.render_module import RenderParameters, RenderModule
from ..TrakEM2.AnnotationJsonSchema import AnnotationFile
from ..shapely import tilespec_to_bounding_box_polygon
from argschema.fields import Str, InputFile
from shapely import geometry
import lxml.etree


parameters={
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":8080,
        "owner":"Forrest",
        "project":"M247514_Rorb_1",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    "stack":"BIGALIGN_LENS_EMclahe_Site3",
    "input_annotation_file":"/nas4/data/EM_annotation/annotationFilesForJHU/m247514_Site3Annotation_cropedToMatch_SD_local.json",
    "output_annotation_file":"/nas4/data/EM_annotation/annotationFilesForJHU/m247514_Site3Annotation_cropedToMatch_SD_global.json"
}


class TransformLocalAnnotationParameters(RenderParameters):
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
    coordinate_mapping = []

    tilespecs = renderapi.tilespec.get_tile_specs_from_stack(stack,render=render)
    #loop over annotations
    for area_list in local_annotation['area_lists']:
        for area in area_list['areas']:
            ts = next(ts for ts in tilespecs if ts.tileId == area['tileId'])
            area['global_path']=renderapi.transform.estimate_dstpts(ts.tforms,area['local_path'])
                    
    return local_annotation


class TransformLocalAnnotation(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = TransformLocalAnnotationParameters
        super(TransformLocalAnnotation,self).__init__(schema_type=schema_type,*args,**kwargs)
    def run(self):

        with open(self.args['input_annotation_file'],'r') as fp:
            local_annotation_json = json.load(fp)
            schema = AnnotationFile()
            local_annotation,errors = schema.load(local_annotation_json)
        #read in the json file
        global_annotation=transform_annotations(self.render,
                              self.args['stack'],
                              local_annotation)

        with open(self.args['output_annotation_file'],'w') as fp:
             json_dict=schema.dump(global_annotation)
             json.dump(json_dict,fp)


if __name__ == "__main__":
    mod = TransformLocalAnnotation(input_data= parameters)
    mod.run()
