if __name__ == "__main__" and __package__ is None:
    __package__ = "renderapps.materialize.make_downsample_image_stack"
import json
import os
import renderapi
from ..module.render_module import RenderModule,RenderParameters
from json_module import InputFile,InputDir,OutputDir
import marshmallow as mm
from functools import partial
import glob
import time
import numpy as np
import time
from PIL import Image
import tifffile
from functools import reduce
import operator


#modified and fixed by Sharmishtaa Seshamani

example_parameters={
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":80,
        "client_scripts":"/var/www/render/render-ws-java-client/src/main/scripts",
		"owner":"S3_Run1",
		"project":"S3_Run1_Master"
    
    },
    "input_stack": "Stitched_DAPI_1_dropped",
    "output_stack": "Stitched_DAPI_1_dropped_Squeezed",
    "output_directory": "/nas3/data/S3_Run1_Igor/processed/tilespecs_squeezed",
    "pool_size":20
}

class SqueezeStackParameters(RenderParameters):
    input_stack = mm.fields.Str(required=True,
        metadata={'description':'input stacks'})
    output_stack = mm.fields.Str(required=True,
        metadata={'description':'output stack to name'})
    output_directory = mm.fields.Str(required=True,
        metadata={'description':'input stacks'})
    pool_size = mm.fields.Int(required=False,default=20,
        metadata={'description':'number of parallel threads to use'})
    
def process_z(stack,render,output_directory,Z):
	
	tilespecs = renderapi.tilespec.get_tile_specs_from_z(stack,Z[0],render=render)
	for ts in tilespecs:
		t = ts.to_dict()
		t['z'] = Z[1]
		ts.from_dict(t)

	tilespecfilename = os.path.join(output_directory,'tilespec_%04d.json'%Z[1])
	print tilespecfilename
	fp = open(tilespecfilename,'w')
	json.dump([ts.to_dict() for ts in tilespecs] ,fp,indent=4)
	fp.close()
    
        

class SqueezeStack(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = SqueezeStackParameters
        super(SqueezeStack,self).__init__(schema_type=schema_type,*args,**kwargs)
    def run(self):
		render=self.render
		if not os.path.exists(self.args['output_directory']):
			os.mkdir(self.args['output_directory'])
		z = self.render.run(renderapi.stack.get_z_values_for_stack,self.args['input_stack'])
		newz = range(0,len(z))
		Z = []
        	for i in range(0,len(z)):
			Z.append( [z[i], newz[i]])

		mypartial = partial(process_z,self.args['input_stack'],render,self.args['output_directory'])
		with renderapi.client.WithPool(self.args['pool_size']) as pool:
			pool.map(mypartial,Z)
		
		outstack = self.args['output_stack']
		jsonfiles = glob.glob("%s/*.json"%self.args['output_directory'])    
        	renderapi.stack.create_stack(outstack,render=self.render,cycleNumber=10,cycleStepNumber=1)
		renderapi.client.import_jsonfiles_parallel(outstack,jsonfiles,render=self.render)


if __name__ == "__main__":
    mod = SqueezeStack(input_data=example_parameters)
    #mod = SqueezeStack(schema_type=MakeDownsampleSectionStackParameters)
    mod.run()
