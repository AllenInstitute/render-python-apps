if __name__ == "__main__" and __package__ is None:
    __package__ = "renderapps.rough_align.ApplyLowRes2HighRes"
import json
import os
import renderapi
from ..module.render_module import RenderModule,RenderParameters
#from json_module import InputFile,InputDir,OutputDir
#import marshmallow as mm
from functools import partial
import glob
import time
import numpy as np
from argschema.fields import InputFile, InputDir, Str, Float, Int


#Author: Sharmishtaa Seshamani

example_parameters={
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":80,
        "owner":"S3_Run1",
        "project":"S3_Run1_Jarvis",
        "client_scripts":"/var/www/render/render-ws-java-client/src/main/scripts"
    },
    'input_stack':'Stitched_Gephyrin_dropped',
    'prealigned_stack': 'Stitched_DAPI_1_dropped',
    'lowres_stack':'Stitched_DAPI_1_Lowres_68_to_223_RoughAlign_filter1_round1111_FIXED_CONS',
    'output_stack':'Rough_Aligned_68_to_112_Gephyrin',
    'tilespec_directory':'/nas4/data/S3_Run1_Jarvis/processed/RoughAlign_filter1_round1111_Gephyrin_test',
    'pool_size':5,
	'scale': 0.05
}

class ApplyLowRes2HighResParameters(RenderParameters):
    input_stack = Str(required=True,
        metadata={'description':'stitched stack to apply alignment to'})
    lowres_stack = Str(required=True,
        metadata={'description':'low res alignmed stack'})
    output_stack = Str(required=True,
        metadata={'description':'output highres aligned stack'})
    prealigned_stack = Str(required=True,
        metadata={'description':'pre aligned stack (typically the one with dropped tiles corrected for stitching errors)'})
    scale = Float(required=False,default = .01,
        metadata={'description':'scale to make images'})
    tilespec_directory = Str(required=True,
        metadata={'decription','path to save section images'})
    output_stack = Str(required=True,
        metadata={'description':'output stack to name'})
    pool_size = Int(required=False,default=20,
        metadata={'description':'number of parallel threads to use'})
    minZ = Int(required=False,default=0,
        metadata={'description':'Minimum Z value'})
    maxZ = Int(required=False,default=100000000,
        metadata={'description':'Maximum Z value'})

def process_z(render,stack,lowres_stack,output_stack,prealigned_stack,output_dir,scale,project,Z):

    z = Z[0]; newz = Z[1]

    try:
		print "A"
		lowres_ts = renderapi.tilespec.get_tile_specs_from_z(lowres_stack,newz,render=render)
		#highres_ts = renderapi.tilespec.get_tile_spec(stack,lowres_ts[0].tileId,render=render)
		highres_ts = renderapi.tilespec.get_tile_specs_from_z(stack,z,render=render)[0]
		tforms = lowres_ts[0].tforms
		print "B"
		d = tforms[0].to_dict()
                dsList = d['dataString'].split()
                v0 = float(dsList[0])*scale
                v1 = float(dsList[1])*scale
                v2 = float(dsList[2])*scale
                v3 = float(dsList[3])*scale
                v4 = float(dsList[4])
                v5 = float(dsList[5])
                d['dataString'] = "%f %f %f %f %s %s"%(v0,v1,v2,v3, v4,v5)
                tforms[0].from_dict(d)
		print "C"
		stackbounds = renderapi.stack.get_bounds_from_z(stack,z,render=render)
                prestackbounds = renderapi.stack.get_bounds_from_z(prealigned_stack,z,render=render)
                tx =  int(stackbounds['minX']) - int(prestackbounds['minX'])
                ty =  int(stackbounds['minY']) - int(prestackbounds['minY'])
		print "D"
		tforms1 = highres_ts.tforms
                d = tforms1[0].to_dict()
                dsList = d['dataString'].split()
                v0 = 1.0
                v1 = 0.0
                v2 = 0.0
                v3 = 1.0
                v4 = tx
                v5 = ty
                d['dataString'] = "%f %f %f %f %s %s"%(v0,v1,v2,v3, v4,v5)
                tforms1[0].from_dict(d)

		print "E"

		#invert orig transformations
		#tform_orig = highres_ts.tforms
		#tform_orig_inv = list(tform_orig)
		#tform_orig_inv.reverse()
		#tform_orig_inv = [tf.invert() for tf in tform_orig_inv]
		#final tform
		#ftform = tform_orig_inv + tforms
		ftform = tforms1 + tforms
		print "F"
		allts = []
		highres_ts1 = renderapi.tilespec.get_tile_specs_from_z(stack,z,render=render)

		for t in highres_ts1:
			print "f1"
			t.tforms.append(ftform)
			print "f2"
			d1 = t.to_dict()
			print "f3"
			print d1['mipmapLevels'][0]['imageUrl']
			d1['z'] = newz
			t.from_dict(d1)
			allts.append(t)
			print d1
    		print "G"

		tilespecfilename = os.path.join(output_dir,'tilespec_%04d.json'%newz)
		print tilespecfilename
		fp = open(tilespecfilename,'w')
		json.dump([ts.to_dict() for ts in allts] ,fp,indent=4)
		fp.close()
    except:
		print "This z has not been aligned!"




class ApplyLowRes2HighRes(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = ApplyLowRes2HighResParameters
        super(ApplyLowRes2HighRes,self).__init__(schema_type=schema_type,*args,**kwargs)
    def run(self):
        allzvalues = self.render.run(renderapi.stack.get_z_values_for_stack,
            self.args['input_stack'])

        allzvalues = np.array(allzvalues)
        zvalues = allzvalues[(allzvalues >= self.args['minZ']) & (allzvalues <=self.args['maxZ'])]


        newzvalues = range(0,len(zvalues))
        Z = []
        for i in range(0,len(zvalues)):
			Z.append( [zvalues[i], newzvalues[i]])

        render=self.render
        if not os.path.exists(self.args['tilespec_directory']):
            os.makedirs(self.args['tilespec_directory'])

        mypartial = partial(process_z,self.render,self.args['input_stack'],
            self.args['lowres_stack'],self.args['output_stack'],self.args['prealigned_stack'],self.args['tilespec_directory'],self.args['scale'],self.args['render']['project'])
        with renderapi.client.WithPool(self.args['pool_size']) as pool:
            pool.map(mypartial,Z)

        jsonfiles = glob.glob("%s/*.json"%self.args['tilespec_directory'])
        renderapi.stack.create_stack(self.args['output_stack'],cycleNumber=11,cycleStepNumber=1, render=self.render)
        renderapi.client.import_jsonfiles_parallel(self.args['output_stack'],jsonfiles,render=self.render)



if __name__ == "__main__":
    #mod = ApplyLowRes2HighRes(input_data=example_parameters)
    mod = ApplyLowRes2HighRes(schema_type =ApplyLowRes2HighResParameters)
    mod.run()
