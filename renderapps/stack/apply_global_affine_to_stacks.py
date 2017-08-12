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
        "port":8080,
        "owner":"Forrest",
        "project":"M247514_Rorb_1",
        "client_scripts":"/var/www/render/render-ws-java-client/src/main/scripts"
    },
    "input_stacks":["LENS_REG_MARCH_21_PSD95_deconvnew","LENS_REG_MARCH_21_MBP_deconvnew","LENS_REG_MARCH_21_DAPI_1_deconvnew","LENS_REG_MARCH_21_DAPI_3_deconvnew"],
    "output_prefix":"BIG",
    "transformId":"expand_lm_to_em_and_rotate",
    "M00":0.0,
    "M10":-33.333,
    "M01":33.333,
    "M11":0.0,
    "B0": 0,  
    "B1": 0,
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
            mod=ApplyAffine(input_data = params)
            mod.run()

if __name__ == "__main__":
    mod = ApplyAffineMultiple(input_data= example_parameters)
    mod.run()
