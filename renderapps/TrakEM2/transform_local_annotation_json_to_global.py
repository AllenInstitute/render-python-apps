import renderapi
import json
import os
from ..module.render_module import RenderParameters, RenderModule
from ..TrakEM2.AnnotationJsonSchema import AnnotationFile
from ..shapely import tilespec_to_bounding_box_polygon
from argschema.fields import Str, InputFile
from shapely import geometry
import lxml.etree
import numpy as np

example_input={
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":8080,
        "owner":"Forrest",
        "project":"M247514_Rorb_1",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    "stack":"Site3Align2_EM_clahe_mm",
    "input_annotation_file":"/nas3/data/M247514_Rorb_1/annotation/m247514_Site3Annotation_MN_local.json",
    "output_annotation_file":"/nas3/data/M247514_Rorb_1/annotation/m247514_Site3Annotation_MN_global.json"
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
            tileIds = np.unique(area['tileIds'])
            lp = area['local_path']
            global_path = np.zeros(lp.shape,lp.dtype)
            for tileId in tileIds:
                ts = next(ts for ts in tilespecs if ts.tileId == tileId)
                ind = np.where(area['tileIds']==tileId)[0]
                global_path[ind,:]= renderapi.transform.estimate_dstpts(ts.tforms,lp[ind,:]) 
            area['global_path']=global_path
            area['z']=ts.z
                    
    return local_annotation


class TransformLocalAnnotation(RenderModule):
    default_schema = TransformLocalAnnotationParameters
    default_output_schema = AnnotationFile
    
    def run(self):
        with open(self.args['input_annotation_file'],'r') as fp:
            local_annotation_json = json.load(fp)
            schema = AnnotationFile()
            local_annotation,errors = schema.load(local_annotation_json)
        #read in the json file
        global_annotation=transform_annotations(self.render,
                              self.args['stack'],
                              local_annotation)
        self.output(global_annotation, self.args['output_annotation_file'])


if __name__ == "__main__":
    mod = TransformLocalAnnotation(input_data= example_input)
    mod.run()
