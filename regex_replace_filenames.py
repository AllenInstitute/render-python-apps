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
import re
#An example set of parameters for this module
example_parameters = {
	"render":{
		"host":"em-131fs",
		"port":8080,
		"owner":"gayathri",
		"project":"EM_Phase1",
		"client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
	},
  "input_stack":"Pinky40_20170313",
  "output_stack":"Pinky40_20170313_aibsdata",
  "regex_find":"em-131fs",
  "regex_replace":"nc-em"
}


class ReplaceFileNameParameters(RenderParameters):
    input_stack = mm.fields.Str(required=True,metadata={'description':'stack to apply affine to'})
    output_stack = mm.fields.Str(required=False,metadata={'description':'stack to save answer into (defaults to overwriting input_stack)'})
    regex_find = mm.fields.Str(required=True,metadata={'description':'regular expression to search for in imageUrl'})
    regex_replace = mm.fields.Str(required=True,metadata={'description':'regular expression replacement string'})
    pool_size = mm.fields.Int(required=False,default=20,metadata={'description':'size of pool for parallel processing (default=20)'})

class ReplaceFileNames(RenderModule):
    def __init__(self,*args,**kwargs):
        super(ReplaceFileNames,self).__init__(*args,**kwargs)


    @staticmethod
    def process_z(render,input_stack,find,replace,z):
        #get the tilespecs for this Z
        tilespecs = render.run(renderapi.tilespec.get_tile_specs_from_z,input_stack,z)
        p = re.compile(find)

        #loop over the tilespes adding the transform
        for ts in tilespecs:
            mml = ts.ip.mipMapLevels[0]
            old_url = mml.imageUrl
            mml.imageUrl = p.sub(replace,old_url)
            ts.ip.update(mml)

        #open a temporary file
        tid,tfile = tempfile.mkstemp(suffix='.json')
        file = open(tfile,'w')
        #write the file to disk
        renderapi.utils.renderdump(tilespecs,file)
        os.close(tid)
        #return the filepath
        return tfile

    def run(self):
        #mod.run()
        #get the z values in the stack
        zvalues = self.render.run(renderapi.stack.get_z_values_for_stack,self.args['input_stack'])

        #define a function to process one z value

        #output_stack defaults to input_stack
        output_stack = self.args.get('output_stack',self.args['input_stack'])

        #define a processing pool
        pool = Pool(mod.args['pool_size'])
        #define a partial function for processing a single z value
        mypartial = partial(self.process_z,self.render,self.args['input_stack'],self.args['regex_find'],self.args['regex_replace'])
        #get the filepaths of json files in parallel
        json_files = pool.map(mypartial,zvalues)

        if self.args['input_stack'] != output_stack:
            sv = renderapi.stack.get_stack_metadata(self.args['input_stack'],render=self.render)
            renderapi.stack.create_stack(output_stack,render=self.render)
            renderapi.stack.set_stack_metadata(output_stack,sv)

        #import the json_files into the output stack
        renderapi.client.import_jsonfiles_parallel(output_stack,json_files,poolsize=self.args['pool_size'],render=mod.render)

        #clean up the temp files
        [os.remove(tfile) for tfile in json_files]

if __name__ == '__main__':
    #process the command line arguments
    mod = ReplaceFileNames(schema_type=ReplaceFileNameParameters,input_data=example_parameters)
    mod.run()
