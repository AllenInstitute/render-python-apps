if __name__ == "__main__" and __package__ is None:
    __package__ = "renderapps.stack.create_subvolume_stack"
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
from functools import reduce
import operator

#Sharmishtaa Seshamani

example_parameters={
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":80,
        "owner":"S3_Run1",
        "project":"S3_Run1_Rosie",
        "client_scripts":"/var/www/render/render-ws-java-client/src/main/scripts"
    },
    'input_stack':'Rough_Aligned_140_to_141_DAPI_1',
    'output_stack':'Subvolume_Rough_Aligned_140_to_141_DAPI_1',
    'directory' : '/nas2/data/S3_Run1_Rosie/processed/subvolume',
    'minX':-1500,
    'maxX':-500,
    'minY':-5700,
    'maxY':-4700,
    'minZ':0,
    'maxZ':25,
    'pool_size':5
	
}

class CreateSubvolumeStackParameters(RenderParameters):
    input_stack = mm.fields.Str(required=True,
        metadata={'description':'stack to make a downsample version of'})
    scale = mm.fields.Float(required=False,default = .01,
        metadata={'description':'scale to make images'})
    directory = OutputDir(required=True,
        metadata={'decription','path to save section images'})
    #numsectionsfile = mm.fields.Str(required=True,
    #    metadata={'decription','file to save length of sections'})
    output_stack = mm.fields.Str(required=True,
        metadata={'description':'output stack to name'})
    pool_size = mm.fields.Int(required=False,default=20,
        metadata={'description':'number of parallel threads to use'})
    minZ = mm.fields.Int(required=False,default=0,
        metadata={'description':'Minimum Z value'})
    maxZ = mm.fields.Int(required=False,default=100000000,
        metadata={'description':'Maximum Z value'})
    minX = mm.fields.Int(required=True,
        metadata={'description':'Minimum X value'})
    maxX = mm.fields.Int(required=True,
        metadata={'description':'Maximum X value'})
    minY = mm.fields.Int(required=True,
        metadata={'description':'Minimum Y value'})
    maxY = mm.fields.Int(required=True,
        metadata={'description':'Maximum Y value'})
        

def process_z(render,stack,output_dir,minX,maxX,minY,maxY,z):
    
    
    tilespecs = renderapi.tilespec.get_tile_specs_from_minmax_box(stack,z,float(minX),float(maxX),float(minY),float(maxY),render=render)
    #tilespecs = z
    newts = []
    for ts in tilespecs:
		d = ts.to_dict()
		d['minIntensity'] = 1000
		d['maxIntensity'] = 65000
		ts.from_dict(d)
		newts.append(ts)
    return newts
    
    
    
   

class CreateSubvolumeStack(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = CreateSubvolumeStackParameters
        super(CreateSubvolumeStack,self).__init__(schema_type=schema_type,*args,**kwargs)
    def run(self):
        allzvalues = self.render.run(renderapi.stack.get_z_values_for_stack,
            self.args['input_stack'])
        allzvalues = np.array(allzvalues)
        zvalues = allzvalues[(allzvalues >= self.args['minZ']) & (allzvalues <=self.args['maxZ'])]
        
        render=self.render
        tsarray = []
		
        mypartial = partial(process_z,self.render,self.args['input_stack'],self.args['directory'],self.args['minX'],self.args['maxX'],self.args['minY'],self.args['maxY'])
        
        with renderapi.client.WithPool(self.args['pool_size']) as pool:
            tsarray.append(pool.map(mypartial,zvalues))
            
        #reduce twice
        tsarray = reduce(operator.concat,tsarray)
        tsarray = reduce(operator.concat,tsarray)
        
        renderapi.stack.create_stack(self.args['output_stack'],cycleNumber=6,cycleStepNumber=1,stackResolutionX = 1, stackResolutionY = 1, render=self.render)
        renderapi.client.import_tilespecs_parallel(self.args['output_stack'],tsarray,render=self.render)

        
if __name__ == "__main__":
    #mod = CreateSubvolumeStack(input_data=example_parameters)
    mod = CreateSubvolumeStack(schema_type=CreateSubvolumeStackParameters)
    
    mod.run()
    
