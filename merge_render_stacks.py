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
example_parameters ={
    "render":{
        "host":"em-131fs",
        "port":8999,
        "owner":"gayathri",
        "project":"EM_Phase1",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    "stack2":"manual_align_Phase1Data_3464_3500_forrestfix",
    "stack1":"Pinky40_20170313_aibsdata_flipped_shifted",
    "zmin":3484,
    "zmax":3500,
    "output_stack":"Princeton_manual_align_testmerge",
    "pool_size":20
}


class MergeStackParameters(RenderParameters):
    stack1 = mm.fields.Str(required=True,metadata={'description':'first stack to merge'})
    stack2 = mm.fields.Str(required=True,metadata={'description':'second stack to merge'})
    output_stack = mm.fields.Str(required=True,metadata={'description':'stack to save answer into'})
    zmin = mm.fields.Int(required=False,metadata={'description':'zvalue to start'})
    zmax = mm.fields.Int(required=False,metadata={'description':'zvalue to end'})
    z_intersection = mm.fields.Boolean(required=False,default=False,
        metadata={'description':'only output z values that appears in both stacks\
        (default False, output z values in either stack)'})
    pool_size = mm.fields.Int(required=False,default=20,metadata={'description':'size of pool for parallel processing (default=20)'})

if __name__ == '__main__':
    #process the command line arguments
    mod = RenderModule(schema_type=MergeStackParameters,input_data=example_parameters)
    mod.run()
    #get the z values in the stack
    zvalues1 = mod.render.run(renderapi.stack.get_z_values_for_stack,mod.args['stack1'])
    zvalues1 = np.array(zvalues1)
    zvalues2 = mod.render.run(renderapi.stack.get_z_values_for_stack,mod.args['stack2'])
    zvalues2 = np.array(zvalues1)

    zmin = mod.args.get('zmin',min(np.min(zvalues1),np.min(zvalues2)))
    zmax = mod.args.get('zmax',min(np.max(zvalues1),np.max(zvalues2)))
    zvalues1 = zvalues1[zvalues1>=zmin]
    zvalues1 = zvalues1[zvalues1<=zmax]
    zvalues2 = zvalues1[zvalues2>=zmin]
    zvalues2 = zvalues1[zvalues2<=zmax]
    if mod.args['z_intersection']:
        zvalues = np.intersect1d(zvalues1,zvalues2)
    else:
        zvalues = np.union1d(zvalues1,zvalues2)

    #define a function to process one z value
    def process_z(render,stack1,stack2,z):
        #get the tilespecs for this Z
        tilespecs1 = render.run( renderapi.tilespec.get_tile_specs_from_z,
                                stack1,
                                z)

        tilespecs2 = render.run( renderapi.tilespec.get_tile_specs_from_z,
                                stack2,
                                z)
        tilespecs = tilespecs1 + tilespecs2
        #open a temporary file
        tid,tfile = tempfile.mkstemp(suffix='.json')
        file = open(tfile,'w')
        #write the file to disk
        renderapi.utils.renderdump(tilespecs,file)
        os.close(tid)

        #return the filepath
        return tfile



    #define a processing pool
    #pool = Pool(mod.args['pool_size'])
    #define a partial function for processing a single z value
    mypartial = partial(process_z,
                        mod.render,
                        mod.args['stack1'],
                        mod.args['stack2'])
    #get the filepaths of json files in parallel
    #json_files = []
    #for z in zvalues:
    #    print z
    #    json_files.append(mypartial(z))
    #print json_files
    pool = Pool(mod.args['pool_size'])
    json_files = pool.map(mypartial,zvalues)
    #import the json_files into the output stack
    output_stack = mod.args['output_stack']
    mod.render.run(renderapi.stack.create_stack,output_stack)

    renderapi.client.import_jsonfiles_parallel( output_stack,
                                                json_files,
                                                poolsize=mod.args['pool_size'],
                                                render=mod.render)

    #clean up the temp files
    [os.remove(tfile) for tfile in json_files]
