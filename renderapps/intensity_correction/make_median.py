if __name__ == "__main__" and __package__ is None:
    __package__ = "renderapps.intensity_correction.make_median"
import json
import os
import renderapi
from ..module.render_module import RenderModule, RenderParameters
from argschema.fields import InputFile, InputDir, Str, Float, Int
from functools import partial
import glob
import time
import numpy as np
import time
from PIL import Image
import tifffile


class MakeMedianParams(RenderParameters):
    input_stack = Str(required=True,
        metadata={'description':'Input stack'})
    output_stack = Str(required=True,
        metadata={'description':'Output stack'})
    minZ = Int(required=True,
        metadata={'description':'z value for section'})
    maxZ = Int(required=True,
        metadata={'description':'z value for section'})

def getImage(ts):
    img0 = tifffile.imread(ts.imageUrl)
    (N,M)=img0.shape
    return N,M,img0

def populateStack(Stack,ts):
    N,M,img = getImage(ts)
    Stack.append(img)

class MakeMedian(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = MakeMedianParams
        super(MakeMedian,self).__init__(schema_type=schema_type,*args,**kwargs)

    def run(self):

        minZ = self.args['minZ']
        maxZ = self.args['maxZ']

        #get tilespecs for z
        alltilespecs = []
        numtiles = 0
        for z in range(minZ,maxZ):
            tilespecs = self.render.run(renderapi.stack.get_tile_specs_from_z,self.args['input_stack'],z)
            alltilespecs.extend(tilespecs)
            #read first image and setup stack
            N,M,img0 = getImage(tilespecs[0])
            numtiles += len(tilespecs)

        #read images and create stack
        stack = np.zeros((N,M,numtiles),dtype=img0.dtype)
        render=self.render
        mypartial = partial(populateStack,self.render,stack)
        with renderapi.client.WithPool(self.args['pool_size']) as pool:
            pool.map(mypartial,alltilespecs)

        #calculate MakeMedian
        np.median(stack,axis=2,overwrite_input=True)
		(A,B,C)=stack.shape

		if (j%2 == 0):
			med1 = stack[:,:,j/2-1]
			med2 = stack[:,:,j/2+1]
			med = (med1+med2)/2
		else:
			med = stack[:,:,(j-1)/2]

		med = gaussian_filter(med,10)


        #save median to file
        tsdir = os.path.dirname(alltilespecs[0].imageUrl)
        [projdir,post] = tsdir.split("raw")
        outdir = "%s/processed/Median/"%projdir
        if not os.path.exists(outdir):
			os.makedirs(outdir)
        outImage = outdir + "Median_%s_%d.tif"%(self.args['input_stack'], self.args['z'])
		tifffile.imsave(outImage,med)

        #create tilespec
        ts = alltilespecs[0]
        ts.z = minZ
        ts.imageUrl = outImage

        #create render stack
        renderapi.stack.create_stack(self.args['output_stack'],cycleNumber=2,cycleStepNumber=1,render=self.render)
        renderapi.client.import_tilespecs(self.args['output_stack'],[ts])
        #renderapi.client.import_jsonfiles_parallel(self.args['output_stack'],[jsonfile],render=self.render)

if __name__ == "__main__":
    mod = MakeMedian(schema_type=MakeMedianParams)
    mod.run()
