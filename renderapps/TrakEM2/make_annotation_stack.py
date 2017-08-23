
# In[133]:


from pandas.io.json import json_normalize 
import renderapi
import os
import json
import cv2
import numpy as np
from pathos.multiprocessing import Pool
from functools import partial
from ..module.render_module import RenderModule, RenderParameters
import argschema
import marshmallow as mm
from AnnotationJsonSchema import AnnotationFile

example_json={
        "render":{
            "host":"ibs-forrestc-ux1",
            "port":8080,
            "owner":"Forrest",
            "project":"M247514_Rorb_1",
            "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
        },
        "input_stack":"BIGALIGN_LENS_EMclahe_all",
        "annotation_stack":"BIGALIGN_LENS_EMannotation_Site3SD",
        "global_file":"/nas4/data/EM_annotation/annotationFilesForJHU/m247514_Site3Annotation_cropedToMatch_SD_global.json",
        "annotation_dir":"/nas4/data/EM_annotation/annotationFilesForJHU/m247514_Site3Annotation_cropedToMatch_SD_tiles/"
}
def make_annotation_stack_parameters(render,annotation_dir,global_file,input_stack,annotation_stack):

    if not os.path.isdir(annotation_dir):
        os.makedirs(annotation_dir)

    with open(global_file,'r') as fp:
        json_dict = json.load(fp)
        schema = AnnotationFile()
        annotations,errors=schema.load(json_dict)

    df = pd.DataFrame()

    for area_list in annotations['area_lists']:
        dft = json_normalize(area_list,'areas')
        dft['oid']=area_list['oid']
        dft['id']=area_list['id']
        df=df.append(dft)

    tile_groups=df.groupby('tileId')

    tilespecs = []
    for tileId,dft in tile_groups:
        print tileId
        ts=renderapi.tilespec.get_tile_spec(input_stack,tileId,render=render)
        ann_image = np.zeros((int(ts.width),int(ts.height)),dtype=np.uint8)
        for i,row in dft.iterrows():
            cv2.fillConvexPoly(ann_image,np.int64(row.local_path),255)
        annotation_tile_image_filename = os.path.join(annotation_dir,"%s_annotation.png"%(ts.tileId))
        mml = renderapi.tilespec.MipMapLevel(level=0,imageUrl=annotation_tile_image_filename)
        ip = renderapi.tilespec.ImagePyramid([mml])
        ts.ip = ip
        tilespecs.append(ts)
        cv2.imwrite(annotation_tile_image_filename,ann_image)

    sv = renderapi.stack.get_stack_metadata(input_stack,render=render)
    renderapi.stack.create_stack(annotation_stack,render=render)
    renderapi.client.import_tilespecs_parallel(annotation_stack,tilespecs,render=render)
    renderapi.set_stack_metadata(annotation_stack,sv,render=render)
    renderapi.stack.set_stack_state(annotation_stack,'COMPLETE',render=render)

class MakeAnnotationStackParameters(RenderParameters):
    input_stack = argschema.fields.Str(required=True,
        description='Render stack which was annotated')
    annotation_stack = argschema.fields.Str(required=True,
        description='Render stack name to save stack into')
    global_file = argschema.fields.InputFile(required=True,
        description='json file path where annotations are saved')
    annotation_dir = argschema.fields.Str(required=True,
        description='path where to save annotation tiles')
        
class MakeAnnotationStack(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = MakeAnnotationStackParameters
        super(MakeAnnotationStack,self).__init__(schema_type=schema_type,*args,**kwargs)
    def run(self):



if __name__ == "__main__":
    mod = MakeAnnotationStack(input_data= example_json)
    mod.run()




