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
		"project":"S3_Run1_Jarvis"
    
    },
    "input_stacks": "Stitched_DAPI_1_Lowres_68_to_112_RoughAlign_filter1_round1111_0_156,Stitched_DAPI_1_Lowres_68_to_112_RoughAlign_filter1_round1111_157_187,Stitched_DAPI_1_Lowres_68_to_112_RoughAlign_filter1_round1111_188_694",
    "input_projects": "S3_Run1_Jarvis,S3_Run1_Jarvis,S3_Run1_Jarvis",
    "output_project": "S3_Run1_Jarvis",
    'output_stack':'Stitched_DAPI_1_Lowres_68_to_223_RoughAlign_filter1_round1111_concat',
    "output_directory":"/nas4/data/S3_Run1_Jarvis/processed/tilespecs_for_concat_roughalign",
    "adjust_z": True,
    'pool_size':20
}

class ConcatenateStacksParameters(RenderParameters):
    input_stacks = mm.fields.Str(required=True,
        metadata={'description':'input stacks'})
    input_projects = mm.fields.Str(required=True,
        metadata={'description':'input projects '})
    output_stack = mm.fields.Str(required=True,
        metadata={'description':'output stack to name'})
    output_project = mm.fields.Str(required=True,
        metadata={'description':'output project'})
    output_directory = mm.fields.Str(required=True,
        metadata={'description':'input stacks'})
    pool_size = mm.fields.Int(required=False,default=20,
        metadata={'description':'number of parallel threads to use'})
    adjust_z = mm.fields.Bool(required=False,default=False,        
	metadata={'description':'whether to adjust z values'})
	
    
def process_z(stack,project,render,output_directory,z):
	print z
	tilespecs = renderapi.tilespec.get_tile_specs_from_z(stack,z,render=render,project=project)
	tilespecfilename = os.path.join(output_directory,'tilespec_%04d.json'%z)
	print tilespecfilename
	fp = open(tilespecfilename,'w')
	json.dump([ts.to_dict() for ts in tilespecs] ,fp,indent=4)
	fp.close()
    

def process_z_adjust(stack,project,render,output_directory,Z):
	print Z[0]
	tilespecs = renderapi.tilespec.get_tile_specs_from_z(stack,Z[0],render=render,project=project)

	for ts in tilespecs:
		d = ts.to_dict()
		d['z'] = Z[1]
		ts.from_dict(d)

	tilespecfilename = os.path.join(output_directory,'tilespec_%04d.json'%Z[1])
	print tilespecfilename
	fp = open(tilespecfilename,'w')
	json.dump([ts.to_dict() for ts in tilespecs] ,fp,indent=4)
	fp.close()
        

class ConcatenateStacks(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = ConcatenateStacksParameters
        super(ConcatenateStacks,self).__init__(schema_type=schema_type,*args,**kwargs)
    def run(self):
		i_st = self.args['input_stacks'].split(',')  
		i_pr = self.args['input_projects'].split(',')
		render=self.render
		tsarray = []
		lastz = -1;
		if not os.path.exists(self.args['output_directory']):
			os.mkdir(self.args['output_directory'])
		for i in range(0,len(i_st)):
			print i
			outstack = self.args['output_stack']+str(i)
			outproject = self.args['output_project']
			self.render.run(renderapi.stack.clone_stack,i_st[i],outstack,toProject=outproject,project=i_pr[i])  
			z = self.render.run(renderapi.stack.get_z_values_for_stack,outstack, project = outproject)
			if self.args['adjust_z'] == True:

				newz = range(lastz+1,lastz+1+len(z))
				Z = []
				for i in range(0,len(z)):
					Z.append([z[i],newz[i]])

				mypartial = partial(process_z_adjust,outstack,outproject,render,self.args['output_directory'])
				with renderapi.client.WithPool(self.args['pool_size']) as pool:
					pool.map(mypartial,Z)

				lastz = newz[len(newz)-1]
				
			else:
				mypartial = partial(process_z,outstack,outproject,render,self.args['output_directory'])
				with renderapi.client.WithPool(self.args['pool_size']) as pool:
					pool.map(mypartial,z)

		print self.args['adjust_z']
		outstack = self.args['output_stack']
		jsonfiles = glob.glob("%s/*.json"%self.args['output_directory'])    
        	renderapi.stack.create_stack(outstack,render=self.render,cycleNumber=10,cycleStepNumber=1,project=outproject)
		renderapi.client.import_jsonfiles_parallel(outstack,jsonfiles,render=self.render,project=outproject)

if __name__ == "__main__":
    #mod = ConcatenateStacks(input_data=example_parameters)
    mod = ConcatenateStacks(schema_type=MakeDownsampleSectionStackParameters)
    mod.run()
