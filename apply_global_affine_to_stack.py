#!/usr/bin/env python
import renderapi 
from renderapi.transform import AffineModel
import json
from render_module import RenderModule,RenderParameters
from pathos.multiprocessing import Pool
from functools import partial
import tempfile
import marshmallow as mm
import os
#An example set of parameters for this module
example_parameters = {
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":8080,
        "owner":"Forrest",
        "project":"M247514_Rorb_1",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    'input_stack':'EM_Site4_stitched',
    'output_stack':'EM_Site4_stitched',
    'M00':1,
    'M10':0,
    'M01':0,
    'M11':1,
    'B0':2*15294,
    'B1':-2*1515,
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
    pool_size = mm.fields.Int(required=False,default=20,metadata={'description':'size of pool for parallel processing (default=20)'})

if __name__ == '__main__':
    #process the command line arguments
    mod = RenderModule(schema_type=ApplyAffineParameters,input_data=example_parameters)
    #mod.run()
    #get the z values in the stack
    zvalues = mod.render.run(renderapi.stack.get_z_values_for_stack,mod.args['input_stack'])

    #define a function to process one z value
    def process_z(render,input_stack,tform,z):
        #get the tilespecs for this Z
        tilespecs = render.run(renderapi.tilespec.get_tile_specs_from_z,input_stack,z)
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

    #define the affine transform to apply everywhere
    global_tform = AffineModel(M00=mod.args['M00'],
                        M10=mod.args['M10'],
                        M01=mod.args['M01'],
                        M11=mod.args['M11'],
                        B0=mod.args['B0'],
                        B1=mod.args['B1'])

    #output_stack defaults to input_stack
    output_stack = mod.args.get('output_stack',mod.args['input_stack'])

    #define a processing pool
    pool = Pool(mod.args['pool_size'])
    #define a partial function for processing a single z value
    mypartial = partial(process_z,mod.render,mod.args['input_stack'],global_tform)
    #get the filepaths of json files in parallel
    json_files = pool.map(mypartial,zvalues)
    #import the json_files into the output stack
    renderapi.client.import_jsonfiles_parallel(output_stack,json_files,poolsize=mod.args['pool_size'],render=mod.render)

    #clean up the temp files
    [os.remove(tfile) for tfile in json_files]