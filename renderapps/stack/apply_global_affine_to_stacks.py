#!/usr/bin/env python
import renderapi
from renderapi.transform import AffineModel, ReferenceTransform
from ..module.render_module import RenderModule, RenderParameters
from apply_global_affine_to_stack import ApplyAffine
from functools import partial
import tempfile
import os
import numpy as np
from argschema.fields import Str, Float, Int
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
    'input_stacks':[],
    'output_prefix':'BIG',
    'M00':33.0,
    'M10':0,
    'M01':0,
    'M11':33.0,
    'B0':0,
    'B1':0,
    'pool_size':2
}

class ApplyAffineMultipleParameters(RenderParameters):
    input_stacks = List(Str,required=True,description='list of stacks to apply affine to')
    output_prefix = Str(required=False,description='prefix to prepend to stack name when saving answer (defaults to overwriting input_stack)')
    M00 = Float(required=False,default=1.0,description='M00 (x\'=M00*x element of affine (default 1.0)')
    M10 = Float(required=False,default=0.0,description='M10 (y\'=M10*x element of affine (default 0.0)')
    M01 = Float(required=False,default=0.0,description='M01 (x\'=M01*y element of affine (default 0.0)')
    M11 = Float(required=False,default=1.0,description='M11 (y\'=M11*y) element of affine (default 1.0)')
    B0 = Float(required=False,default=0.0,description='B0 (x translation) element of affine (defautl 0.0)')
    B1 = Float(required=False,default=0.0,description='B1 (y translation) element of affine (default 0.0)')
    zmin = Int(required=False,description='zvalue to start')
    zmax = Int(required=False,description='zvalue to end')
    pool_size = Int(required=False,default=20,description='size of pool for parallel processing (default=20)')

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

        zvalues = self.render.run(renderapi.stack.get_z_values_for_stack,self.args['input_stack'])
        zvalues = np.array(zvalues)
        print(zvalues)
        zmin = self.args.get('zmin',np.min(zvalues))
        zmax = self.args.get('zmax',np.max(zvalues))
        zvalues = zvalues[zvalues>=zmin]
        zvalues = zvalues[zvalues<=zmax]



        #output_stack defaults to input_stack
        input_stack = self.args['input_stack']
        output_stack = self.args.get('output_stack',input_stack)

        tformid = '{}_to_{}'.format(input_stack,output_stack)

        #define the affine transform to apply everywhere
        global_tform = AffineModel(M00=self.args['M00'],
                            M10=self.args['M10'],
                            M01=self.args['M01'],
                            M11=self.args['M11'],
                            B0=self.args['B0'],
                            B1=self.args['B1'])
        #global_tform_ref = ReferenceTransform(refId=tformid)
       
        #define a processing pool
        #pool = Pool(self.argsargs['pool_size'])
        #define a partial function for processing a single z value
        
        #make the first json fiel with the actual transform
        #tform_0 = process_z(self.render, input_stack,global_tform,zvalues[0])
        #do the rest using the reference
        mypartial = partial(process_z,
                            self.render,
                            input_stack,
                            global_tform)
        #get the filepaths of json files in parallel
        tforms = []
        for z in zvalues:
            print("{}".format(z))
            tforms+=mypartial(z)

        #print json_files
        #with renderapi.client.WithPool(self.args['pool_size']) as pool:
        #    json_files = pool.map(mypartial,zvalues[1:])
        #tforms += tform_0
        #import the json_files into the output stack
        
        if (self.args['input_stack'] != output_stack):
            self.render.run(renderapi.stack.create_stack,output_stack)

        tid,tfile = tempfile.mkstemp(suffix='.json')
        file = open(tfile,'w')
        #write the file to disk
        json.dump(tforms,file)
        file.close()
        os.close(tid)
        #return the filepath

        renderapi.client.importTransformChangesClient(input_stack,
                                                    output_stack,
                                                    tfile,
                                                    changeMode = 'APPEND',
                                                    poolsize=self.args['pool_size'],
                                                    render=self.render)
        renderapi.stack.set_stack_state(output_stack,'COMPLETE', render=self.render)
        #clean up the temp files
        os.remove(tfile)
        #print json.dumps(tforms,indent=2)
        #print tfile
if __name__ == "__main__":
    mod = ApplyAffine(input_data= example_parameters)
    mod.run()
