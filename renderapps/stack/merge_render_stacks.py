#!/usr/bin/env python
import renderapi
from ..module.render_module import RenderModule, RenderParameters
from functools import partial
import tempfile
import os
import numpy as np
from argschema.fields import Str, Int, Boolean

# An example set of parameters for this module
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


class MergeStacksParameters(RenderParameters):
    stack1 = Str(required=True,metadata={'description':'first stack to merge'})
    stack2 = Str(required=True,metadata={'description':'second stack to merge'})
    output_stack = Str(required=True,metadata={'description':'stack to save answer into'})
    zmin = Int(required=False,metadata={'description':'zvalue to start'})
    zmax = Int(required=False,metadata={'description':'zvalue to end'})
    z_intersection = Boolean(required=False,default=False,
        metadata={'description':'only output z values that appears in both stacks\
        (default False, output z values in either stack)'})
    pool_size = Int(required=False,default=20,metadata={'description':'size of pool for parallel processing (default=20)'})

class MergeStacks(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = MergeStacksParameters
        super(MergeStacks,self).__init__(schema_type=schema_type,*args,**kwargs)
    def run(self):
        print self.args
        self.logger.error('WARNING NEEDS TO BE TESTED, TALK TO FORREST IF BROKEN')
        #get the z values in the stack
        zvalues1 = self.render.run(renderapi.stack.get_z_values_for_stack,self.args['stack1'])
        zvalues1 = np.array(zvalues1)
        zvalues2 = self.render.run(renderapi.stack.get_z_values_for_stack,self.args['stack2'])
        zvalues2 = np.array(zvalues1)

        zmin = self.args.get('zmin',min(np.min(zvalues1),np.min(zvalues2)))
        zmax = self.args.get('zmax',min(np.max(zvalues1),np.max(zvalues2)))
        zvalues1 = zvalues1[zvalues1>=zmin]
        zvalues1 = zvalues1[zvalues1<=zmax]
        zvalues2 = zvalues1[zvalues2>=zmin]
        zvalues2 = zvalues1[zvalues2<=zmax]
        if self.args['z_intersection']:
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
        #pool = Pool(self.args['pool_size'])
        #define a partial function for processing a single z value
        mypartial = partial(process_z,
                            self.render,
                            self.args['stack1'],
                            self.args['stack2'])
        #get the filepaths of json files in parallel
        #json_files = []
        #for z in zvalues:
        #    print z
        #    json_files.append(mypartial(z))
        #print json_files
        with renderapi.client.WithPool(self.args['pool_size']) as pool:
            json_files = pool.map(mypartial,zvalues)
        #import the json_files into the output stack
        output_stack = self.args['output_stack']
        self.render.run(renderapi.stack.create_stack,output_stack)

        renderapi.client.import_jsonfiles_parallel( output_stack,
                                                    json_files,
                                                    poolsize=self.args['pool_size'],
                                                    render=self.render)

        #clean up the temp files
        [os.remove(tfile) for tfile in json_files]

if __name__ == "__main__":
    mod = MergeStacks(input_data= example_parameters)
    mod.run()
