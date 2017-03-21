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
import numpy as np
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
    'pool_size':20
}

class RenameSectionIdParameters(RenderParameters):
    input_stack = mm.fields.Str(required=True,metadata={'description':'stack to apply affine to'})
    output_stack = mm.fields.Str(required=False,metadata={'description':'stack to save answer into (defaults to overwriting input_stack)'})
    zmin = mm.fields.Int(required=False,metadata={'description':'zvalue to start'})
    zmax = mm.fields.Int(required=False,metadata={'description':'zvalue to end'})
    pool_size = mm.fields.Int(required=False,default=20,metadata={'description':'size of pool for parallel processing (default=20)'})

if __name__ == '__main__':
    #process the command line arguments
    mod = RenderModule(schema_type=RenameSectionIdParameters,input_data=example_parameters)
    mod.run()
    #get the z values in the stack
    zvalues = mod.render.run(renderapi.stack.get_z_values_for_stack,mod.args['input_stack'])
    zvalues = np.array(zvalues)
    print zvalues
    zmin = mod.args.get('zmin',np.min(zvalues))
    zmax = mod.args.get('zmax',np.max(zvalues))
    zvalues = zvalues[zvalues>=zmin]
    zvalues = zvalues[zvalues<=zmax]

    #define a function to process one z value
    def process_z(render,input_stack,z):
        #get the tilespecs for this Z
        tilespecs = render.run( renderapi.tilespec.get_tile_specs_from_z,
                                input_stack,
                                z)
        #loop over the tilespes adding the transform
        for ts in tilespecs:
            ts.layout.sectionId = "%0.1f"%z
        #open a temporary file
        tid,tfile = tempfile.mkstemp(suffix='.json')
        file = open(tfile,'w')
        #write the file to disk
        renderapi.utils.renderdump(tilespecs,file)
        os.close(tid)
        #return the filepath
        return tfile

    #output_stack defaults to input_stack
    output_stack = mod.args.get('output_stack',mod.args['input_stack'])

    #define a processing pool
    #pool = Pool(mod.args['pool_size'])
    #define a partial function for processing a single z value
    mypartial = partial(process_z,
                        mod.render,
                        mod.args['input_stack'])
    #get the filepaths of json files in parallel
    #json_files = []
    #for z in zvalues:
    #    print z
    #    json_files.append(mypartial(z))
    #print json_files
    pool = Pool(mod.args['pool_size'])
    json_files = pool.map(mypartial,zvalues)
    #import the json_files into the output stack
    if (mod.args['input_stack'] != output_stack):
        mod.render.run(renderapi.stack.create_stack,output_stack)
    mod.render.run(renderapi.stack.set_stack_state,output_stack,'LOADING')


    renderapi.client.import_jsonfiles_parallel( output_stack,
                                                json_files,
                                                poolsize=mod.args['pool_size'],
                                                render=mod.render)

    #clean up the temp files
    [os.remove(tfile) for tfile in json_files]
