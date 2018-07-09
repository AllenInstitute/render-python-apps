#!/usr/bin/env python
import renderapi
from renderapi.transform import AffineModel, ReferenceTransform
from ..module.render_module import RenderModule
from apply_global_affine_to_stack import ApplyAffineParametersBase, ApplyAffine
from functools import partial
import tempfile
import os
import numpy as np
from argschema.fields import Str, Float, Int, List
import json

#An example set of parameters for this module
example_parameters = {
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":80,
        "owner":"Forrest",
        "project":"M246930_Scnn1a_4_f1",
        "client_scripts":"/var/www/render/render-ws-java-client/src/main/scripts"
    },
    "input_stacks":["ROT_FA_STI_DCV_FF_Session1","ROT_FA_STI_DCV_FF_Session2","ROT_FA_STI_DCV_FF_Session3"],
    "output_prefix":"BIG_",
    "transformId":"expand_lm_to_em_and_rotate",
    "M00":0,
    "M10":33.333,
    "M01":-33.333,
    "M11":0,
    "B0": 304867,  
    "B1": 8776,
    "pool_size":2
}

class ApplyAffineMultipleParameters(ApplyAffineParametersBase):
    input_stacks = List(Str,required=True,description='list of stacks to apply affine to')
    output_prefix = Str(required=False,description='prefix to prepend to stack name when saving answer (defaults to overwriting input_stack)')

class ApplyAffineMultiple(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = ApplyAffineMultipleParameters
        super(ApplyAffineMultiple,self).__init__(schema_type=schema_type,*args,**kwargs)

    def run(self):
        #get the z values in the stack
        input_stacks = self.args['input_stacks']
        output_prefix = self.args.get('output_prefix',None)

        for input_stack in input_stacks:
            params = dict(self.args)
            params['input_stack']=input_stack
            if output_prefix is not None:
                params['output_stack']=output_prefix+input_stack

            del params['input_stacks']
            del params['output_prefix']
            if 'input_json' in params.keys():
                del params['input_json']
            print params['input_stack']
            mod=ApplyAffine(input_data = params,args=[])
            mod.run()

if __name__ == "__main__":
    mod = ApplyAffineMultiple(input_data= example_parameters)
    mod.run()
