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
        "owner":"Forrest",
        "project":"M247514_Rorb_1",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    'input_stack':'EM_Site4_stitched',
    'output_stack':'EM_Site4_stitched',
    'pool_size':20
}

class RenameSectionIdsParameters(RenderParameters):
    input_stack = mm.fields.Str(required=True,metadata={'description':'stack to apply affine to'})
    output_stack = mm.fields.Str(required=False,metadata={'description':'stack to save answer into (defaults to overwriting input_stack)'})
    zmin = mm.fields.Int(required=False,metadata={'description':'zvalue to start'})
    zmax = mm.fields.Int(required=False,metadata={'description':'zvalue to end'})
    pool_size = mm.fields.Int(required=False,default=20,metadata={'description':'size of pool for parallel processing (default=20)'})

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

class RenameSectionIds(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = RenameSectionIdsParameters
        super(Template,self).__init__(schema_type=schema_type,*args,**kwargs)
    def run(self):
        print self.args
        self.logger.error('WARNING NEEDS TO BE TESTED, TALK TO FORREST IF BROKEN')

        #get the z values in the stack
        zvalues = self.render.run(renderapi.stack.get_z_values_for_stack,self.args['input_stack'])
        zvalues = np.array(zvalues)
        print zvalues
        zmin = self.args.get('zmin',np.min(zvalues))
        zmax = self.args.get('zmax',np.max(zvalues))
        zvalues = zvalues[zvalues>=zmin]
        zvalues = zvalues[zvalues<=zmax]

        #output_stack defaults to input_stack
        output_stack = self.args.get('output_stack',self.args['input_stack'])

        #define a processing pool
        #pool = Pool(self.args['pool_size'])
        #define a partial function for processing a single z value
        mypartial = partial(process_z,
                            self.render,
                            self.args['input_stack'])
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
            self.render.run(renderapi.stack.create_stack,output_stack)
        self.render.run(renderapi.stack.set_stack_state,output_stack,'LOADING')


        renderapi.client.import_jsonfiles_parallel( output_stack,
                                                    json_files,
                                                    poolsize=self.args['pool_size'],
                                                    render=self.render)

        #clean up the temp files
        [os.remove(tfile) for tfile in json_files]

if __name__ == "__main__":
    mod = RenameSectionIds(input_data= example_json)
    mod.run()
