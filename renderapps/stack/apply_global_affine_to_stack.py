#!/usr/bin/env python
import renderapi
from renderapi.transform import AffineModel
import json
from ..module.render_module import RenderModule,RenderParameters
from functools import partial
import tempfile
import marshmallow as mm
import os
import numpy as np
#An example set of parameters for this module
example_parameters = {
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":8080,
        "owner":"S3_Run1",
        "project":"S3_Run1_Jarvis",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    'input_stack':'Rough_Aligned_DAPI_1',
    'output_stack':'Rough_Aligned_DAPI_1_fullscale',
    'M00':20.0,
    'M10':0.0,
    'M01':0.0,
    'M11':20.0,
    'B0':0.0,
    'B1':0.0,
    'pool_size':20
}

class ApplyAffineParameters(RenderParameters):
    input_stack = mm.fields.Str(required=True,metadata={'description':'stack to apply affine to'})
    output_stack = mm.fields.Str(required=False,metadata={'description':'stack to save answer into (defaults to overwriting input_stack)'})
    M00 = mm.fields.Float(required=False,default=1.0,metadata={'description':'M00 (x\'=M00*x element of affine (default 1.0)'})
    M10 = mm.fields.Float(required=False,default=0.0,metadata={'description':'M10 (y\'=M10*x element of affine (default 0.0)'})
    M01 = mm.fields.Float(required=False,default=0.0,metadata={'description':'M01 (x\'=M01*y element of affine (default 0.0)'})
    M11 = mm.fields.Float(required=False,default=1.0,metadata={'description':'M11 (y\'=M11*y) element of affine (default 1.0)'})
    B0 = mm.fields.Float(required=False,default=0.0,metadata={'description':'B0 (x translation) element of affine (defautl 0.0)'})
    B1 = mm.fields.Float(required=False,default=0.0,metadata={'description':'B1 (y translation) element of affine (default 0.0)'})
    zmin = mm.fields.Int(required=False,metadata={'description':'zvalue to start'})
    zmax = mm.fields.Int(required=False,metadata={'description':'zvalue to end'})
    pool_size = mm.fields.Int(required=False,default=20,metadata={'description':'size of pool for parallel processing (default=20)'})

#define a function to process one z value
def process_z(render,input_stack,tform,z):
    #get the tilespecs for this Z
    tilespecs = render.run( renderapi.tilespec.get_tile_specs_from_z,
                            input_stack,
                            z)
    #loop over the tilespes adding the transform
    for ts in tilespecs:
        ts.tforms.append(tform)
    #open a temporary file
    tid,tfile = tempfile.mkstemp(suffix='.json')
    file = open(tfile,'w')
    #write the file to disk
    renderapi.utils.renderdump(tilespecs,file)
    os.close(tid)
    #return the filepath
    return tfile

class ApplyAffine(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = ApplyAffineParameters
        super(ApplyAffine,self).__init__(schema_type=schema_type,*args,**kwargs)

    def run(self):
        self.logger.error('WARNING NEEDS TO BE TESTED, TALK TO FORREST IF BROKEN')

        #get the z values in the stack
        zvalues = self.render.run(renderapi.stack.get_z_values_for_stack,self.args['input_stack'])
        zvalues = np.array(zvalues)
        print zvalues
        zmin = self.args.get('zmin',np.min(zvalues))
        zmax = self.args.get('zmax',np.max(zvalues))
        zvalues = zvalues[zvalues>=zmin]
        zvalues = zvalues[zvalues<=zmax]  
        #print zvalues
        #define the affine transform to apply everywhere
        global_tform = AffineModel(M00=self.args['M00'],
                            M10=self.args['M10'],
                            M01=self.args['M01'],
                            M11=self.args['M11'],
                            B0=self.args['B0'],
                            B1=self.args['B1'])

        #output_stack defaults to input_stack
        output_stack = self.args.get('output_stack',self.args['input_stack'])

        #define a processing pool
        #pool = Pool(self.args['pool_size'])
        #define a partial function for processing a single z value
        mypartial = partial(process_z,
                            self.render,
                            self.args['input_stack'],
                            global_tform)
        #get the filepaths of json files in parallel
        #json_files = []
        #for z in zvalues:
        #    print z
        #    json_files.append(mypartial(z))
        #print json_files
        with renderapi.client.WithPool(self.args['pool_size']) as pool:
            json_files = pool.map(mypartial,zvalues)
        #import the json_files into the output stack
        if (self.args['input_stack'] != output_stack):
            self.render.run(renderapi.stack.create_stack,output_stack,cycleNumber=11,cycleStepNumber=1)

        renderapi.client.import_jsonfiles_parallel( output_stack,
                                                    json_files,
                                                    poolsize=self.args['pool_size'],
                                                    render=self.render)

        #clean up the temp files
        [os.remove(tfile) for tfile in json_files]


if __name__ == "__main__":
    #mod = ApplyAffine(input_data= example_parameters)
	mod = ApplyAffine(schema_type = ApplyAffineParameters)
	mod.run()
    

    
