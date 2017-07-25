import numpy as np
from renderapi.transform import AffineModel
import json
from functools import partial
import argparse
from renderapi.utils import stripLogger
import os
import renderapi
from ..module.render_module import RenderModule, RenderParameters
from json_module import InputFile, InputDir
import marshmallow as mm
from functools import reduce
import operator
import pandas as pd
import tifffile

#modified by sharmi

example_json={
    "render":{
        "host":"http://ibs-forrestc-ux1",
        "port":80,
        "owner":"S3_Run1",
        "project":"S3_Run1_Master",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    "input_stack":"Rough_Aligned_DAPI_1_fullscale_CONS",
    "output_stack":"Rough_Aligned_DAPI_1_fullscale_CONS_NORM",
    "output_directory":"/nas4/data/S3_Run1_Jarvis/processed/json_tilespecs_consnorm_master",
    "pool_size":20
}



class AutoSetStackLevelsParameters(RenderParameters):
    input_stack = mm.fields.Str(required=True,
        metadata={'description':'stack to consolidate'})
    output_stack = mm.fields.Str(required=True,
        metadata={'description':'stack to consolidate'})
    output_directory = mm.fields.Str(required=True,
        metadata={'description':'outputdirectory'})
    pool_size = mm.fields.Int(required=False, default=20,
        metadata={'description':'name of output stack (default to adding postfix to input)'})


  
def process_z(render,logger,stack,outstack,json_dir,z,N=10):
    def calc_auto_min_max(filepath,logcut=4,mostminus=500):
        data=tifffile.imread(filepath)
        dr=data.ravel()
        (vals,bins)=np.histogram(dr,bins=np.arange(0,2**16,2**7))
        centers = (bins[1:]+bins[:-1])/2
        most = centers[np.argmax(vals)]
        goodones=np.where((centers>most)&(np.log(vals)>4))[0]
        xt =np.log(centers[goodones])
        yt = np.log(vals[goodones])
        ans=np.polyfit(xt,yt,1)
        linfitmax = np.exp((logcut-ans[1])/ans[0])
        return (most-mostminus,linfitmax)

    #tilespecs = render.get_tile_specs_from_z(stack,z)
    tilespecs = renderapi.tilespec.get_tile_specs_from_z(stack,z,render=render)
    randtileindices=np.random.choice(range(len(tilespecs)),N)
    df = pd.DataFrame()
    for index in randtileindices:
        d={}
        
        (minval,maxval)=calc_auto_min_max(tilespecs[0].to_dict()['mipmapLevels'][0]['imageUrl'])
        #d={'minval':minval,'maxval':maxval,'path':tilespecs[index].imageUrl}
        d={'minval':minval,'maxval':maxval,'path':tilespecs[0].to_dict()['mipmapLevels'][0]['imageUrl']}
        
        df=df.append(d,ignore_index=True)
    medians=df.median()
    minval = medians.minval
    maxval = medians.maxval
    for tile in tilespecs:
        tile.minint= minval
        tile.maxint= maxval
    jsonlist=[ts.to_dict() for ts in tilespecs]
    json_path = os.path.join(json_dir,'%s_%05d.json'%(outstack,z))
    json.dump(jsonlist,open(json_path,'w'))
    return json_path
	
class AutoSetStackLevels(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = AutoSetStackLevelsParameters
        super(AutoSetStackLevels,self).__init__(schema_type=schema_type, *args, **kwargs)
    def run(self):
        self.logger.error('Adapted from ipython notebook...........')
        instack = self.args['input_stack']
        outstack= self.args.get('output_stack',None)
        json_dir = self.args['output_directory']
        if not os.path.isdir(json_dir):
            os.makedirs(json_dir)

		
        zvalues = self.render.run(renderapi.stack.get_z_values_for_stack,instack)
        
        render=self.render
        
        mypartial = partial(process_z,self.render, self.logger, instack, outstack, json_dir)
        with renderapi.client.WithPool(self.args['pool_size']) as pool:
            json_files=pool.map(mypartial, zvalues)

        renderapi.stack.delete_stack(outstack,render=self.render)
        renderapi.stack.create_stack(outstack,render=self.render,cycleNumber=13,cycleStepNumber=1)
        renderapi.client.import_jsonfiles_parallel(outstack, json_files,render=self.render)
        
if __name__ == "__main__":
    mod = AutoSetStackLevels(input_data=example_json)
    #mod = AutoSetStackLevels(schema_type=ConsolidateTransformsParameters)
    mod.run()

    
