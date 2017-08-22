if __name__ == "__main__" and __package__ is None:
    __package__ = "renderapps.materialize.make_downsample_image_stack"
import json
import os
import renderapi
from ..module.render_module import RenderModule,RenderParameters
from json_module import InputFile,InputDir,OutputDir
import marshmallow as mm
from functools import partial
import glob
import time
import numpy as np
import time
from PIL import Image
import tifffile

#modified and fixed by Sharmishtaa Seshamani

example_parameters={
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":80,
        "owner":"S3_Run1",
        "project":"S3_Run1_Igor",
        "client_scripts":"/var/www/render/render-ws-java-client/src/main/scripts"
    },
    'input_stack1':'Stitched_DAPI_1',
    'input_stack2':'Stitched_PSD95',

}

class DiffzParameters(RenderParameters):
    input_stack1 = mm.fields.Str(required=True,
        metadata={'description':'stack 1'})
    input_stack2 = mm.fields.Str(required=True,
        metadata={'description':'stack 2'})
    

class Diffz(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = DiffzParameters
        super(Diffz,self).__init__(schema_type=schema_type,*args,**kwargs)
    def run(self):
        zvalues1 = self.render.run(renderapi.stack.get_z_values_for_stack,self.args['input_stack1'])
        zvalues2 = self.render.run(renderapi.stack.get_z_values_for_stack,self.args['input_stack2'])
        
        c = set(zvalues1).union(set(zvalues2))
        d = set(zvalues1).intersection(set(zvalues2))
        
        print list(c-d)
        
       
        
if __name__ == "__main__":
    mod = Diffz(input_data=example_parameters)
    #mod = Diffz(schema_type=DiffzParameters)
    
    mod.run()
    
