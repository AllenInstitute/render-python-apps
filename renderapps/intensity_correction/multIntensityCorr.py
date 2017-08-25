if __name__ == "__main__" and __package__ is None:
    __package__ = "renderapps.intensity_correction.multIntensityCorr"
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


class MultIntensityCorrParams(RenderParameters):
    input_stack = Str(required=True,
        metadata={'description':'Input stack'})
    output_stack = Str(required=True,
        metadata={'description':'Output stack'})
    correction_stack = Str(required=True,
        metadata={'description':'Correction stack (usually median stack for AT data)'})
    output_directory = Str(required=True,
        metadata={'description':'Directory for storing Images'})
    Z = Int(required=True,
        metadata={'description':'z value for section'})

def intensity_corr(img,ff):
        img = img.astype(float)
        ff = ff.astype(float)

        num = np.ones((ff.shape[0],ff.shape[1]))
        fac = np.divide(num* np.amax(ff),ff+0.0001)
        result = np.multiply(img,fac)
        result = np.multiply(result,np.mean(img)/np.mean(result))
        result_int = np.uint16(result)
        return result_int

def getImage(ts):
    img0 = tifffile.imread(ts.imageUrl)
    (N,M)=img0.shape
    return N,M,img0

def process_z(C, dirout, input_ts):
    I = getImage(input_ts)
    Res = intensity_corr(I,C)
    if not os.path.exists(dirout):
        os.makedirs(dirout)
    [head,tail] = os.path.split(input_ts.imageUrl)
    outImage = "%s/%s"%(dirout,tail)
    tifffile.imsave(outImage,Res)

    output_ts = input_ts
    output_ts.imageUrl = outImage
    return output_ts


class MultIntensityCorr(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = MultIntensityCorrParams
        super(MultIntensityCorr,self).__init__(schema_type=schema_type,*args,**kwargs)

    def run(self):

        #get tilespecs
        Z = self.args['Z']
        inp_tilespecs = self.render.run(renderapi.stack.get_tile_specs_from_z,self.args['input_stack'],z)
        corr_tilespecs = self.render.run(renderapi.stack.get_tile_specs_from_z,self.args['correction_stack'],z)

        #mult intensity correct each tilespecs and return tilespecs
        render=self.render
        C = getImage(corr_tilespecs[0]);
        mypartial = partial(process_z,self.render, C)
        with renderapi.client.WithPool(self.args['pool_size']) as pool:
            tilespecs = pool.map(mypartial,inp_tilespecs)

        #upload to render
        renderapi.stack.create_stack(self.args['output_stack'],cycleNumber=2,cycleStepNumber=1,render=self.render)
        renderapi.client.import_tilespecs(self.args['output_stack'],tilespecs)


if __name__ == "__main__":
    mod = MultIntensityCorr(schema_type=MultIntensityCorrParams)
    mod.run()
