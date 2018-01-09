#!/usr/bin/env python
import renderapi
from renderapi.transform import AffineModel, ReferenceTransform
from ..module.render_module import RenderModule, RenderParameters
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
        "owner":"Medium_volume",
        "project":"M335503_R3CBa_Ai139_medvol_run2",
        "client_scripts":"/var/www/render/render-ws-java-client/src/main/scripts"
    },
    "input_stack": "Fine_Aligned_PSD95_fullscale_masked_R7",
    "output_stack":"Fine_Aligned_PSD95_fullscale_masked_R7_R10",
    "mask_file": "/nas2/render_utilities/focusmask/mask_r10.tif",
    "pool_size": 1,
    "minz":553,
    "maxz":585
}

class ApplyMaskParameters(RenderParameters):
    mask_file = Str(required=True,description='Mask file')
    input_stack = Str(required=True,description='Input Stack')
    output_stack = Str(required=True,description='Output Stack')
    pool_size = Int(required=False,default=20,description='size of pool for parallel processing (default=20)')
    minz = Int(required=False,default = -1, description='minz')
    maxz = Int(required=False,default = -1, description='maxz')


#define a function to process one z value
def process_z(render,input_stack,mask_file,z):
    
    changes_list =[]
    #get the tilespecs for this Z
    tilespecs = render.run( renderapi.tilespec.get_tile_specs_from_z,
                            input_stack,
                            z)
    
    #loop over the tilespes adding the transform
    for ts in tilespecs:
	d = ts.to_dict()
	d['mipmapLevels'][0]['maskUrl'] = mask_file
	ts.from_dict(d)        
	changes_list.append(ts)
    output_json_filepath = tempfile.mktemp(suffix='.json')
    with open(output_json_filepath,'w') as fp:
        renderapi.utils.renderdump(changes_list,fp)
    return output_json_filepath
    #return changes_list

class ApplyMask(RenderModule):

    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = ApplyMaskParameters
        super(ApplyMask,self).__init__(schema_type=schema_type,*args,**kwargs)

    def run(self):
	render=self.render
 	input_stack = self.args['input_stack']
        output_stack = self.args['output_stack']
        mask_file = self.args['mask_file']
	minz = self.args['minz']
	maxz = self.args['maxz']
	zvalues = []
	allzvalues = self.render.run(renderapi.stack.get_z_values_for_stack,self.args['input_stack'])
        #get the z values in the stack
	if (minz>=0) and (maxz >=0):
		print "sub z exist" 
		for i in range(minz,maxz):
			if i in allzvalues:
		#if range(minz, maxz) in allzvalues:
        			zvalues.append(i)
				print 'added new z'
			else:
				print " this z value does not exist:" + str(i)

	else:	
		#print zvalues
		zvalues = allzvalues
	print zvalues
        
	
        mypartial = partial(process_z,render,input_stack,mask_file)
	with renderapi.client.WithPool(self.args['pool_size']) as pool:
		jsonFilePaths = pool.map(mypartial, zvalues)
	
	print len(jsonFilePaths)

        if (self.args['input_stack'] != output_stack):
            self.render.run(renderapi.stack.clone_stack,input_stack, output_stack)
        print "cloned stack"
	self.render.run(renderapi.client.import_jsonfiles_parallel,output_stack, jsonFilePaths)
        self.render.run(renderapi.stack.set_stack_state,output_stack,state='COMPLETE')
	print "updated stack"
	
	#renderapi.client.import_tilespecs_parallel(output_stack,newts,render=self.render)  
        #sv = renderapi.stack.get_stack_metadata(input_stack, render=self.render)
        #renderapi.stack.set_stack_metadata(output_stack,sv, render=self.render)
        #renderapi.stack.set_stack_state(output_stack,'COMPLETE', render=self.render)
        
if __name__ == "__main__":
    mod = ApplyMask(input_data= example_parameters)
    mod.run()
