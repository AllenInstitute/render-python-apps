if __name__ == "__main__" and __package__ is None:
    __package__ = "renderapps.intensity_correction.apply_deconvolution"
import os
import renderapi
from ..module.render_module import RenderModule, RenderParameters
from argschema.fields import InputFile, InputDir, Str, Float, Int, Bool
from functools import partial
import numpy as np
from skimage.morphology import disk
import cv2
import tifffile
from deconvtools import deconvlucy

example_input = {
    "render": {
        "host": "ibs-forrestc-ux1",
        "port": 8080,
        "owner": "6_ribbon_expts",
        "project": "M335503_Ai139_smallvol",
        "client_scripts": "/var/www/render/render-ws-java-client/src/main/scripts"
    },
    "input_stack": "Flatfieldcorrected_1_GFP",
    "output_stack": "Deconvolved_1_GFP",
    "output_directory": "/nas2/data/M335503_Ai139_smallvol/processed/Deconvolved",
    "z_index": 400,
    "pool_size": 20,
    "psf_file": "/nas2/data/M335503_Ai139_smallvol/processed/psfs/psf_GFP.tif",
    "num_iter": 20,
    "bgrd_size": 50,
    "scale_factor": 1
}

class ApplyDeconvParams(RenderParameters):
    input_stack = Str(required=True, 
                      description='Input stack')
    output_stack = Str(required=True, 
                       description='Output stack')
    output_directory = Str(required=True, 
                           description='Directory for storing Images')
    z_index = Int(required=True, 
                  description='z value for section')
    pool_size = Int(required=False, default=20, 
                    description='size of pool for parallel processing (default=20)')
    psf_file = InputFile(required=True, 
                         description='path to psf file')
    num_iter = Int(required=True, default=20,
                  description='number of iterations (default=20)')
    bgrd_size = Int(required=False, default=20, 
                    description='size of rolling ball (default=20)')
    scale_factor = Int(required=False, default=1, 
                    description='scaling factor (default=1)')
    close_stack = Bool(required=False, default=False,
                       description="whether to close stack or not")

def getImage(ts):
    d = ts.to_dict()
    img = tifffile.imread(d['mipmapLevels'][0]['imageUrl'])
    img = img.astype(float)
    return img

def getPSF(filename):
    psf = tifffile.imread(filename)
    psf = psf.astype(float)
    psf = psf/np.sum(psf)
    return psf

#def subtract_bgrd(img, bgrd_size):
#     if not bgrd_size == 0:
#         img = cv2.morphologyEx(img,cv2.MORPH_TOPHAT,disk(bgrd_size))

def process_tile(psf, num_iter, bgrd_size, scale_factor, dirout, stackname, input_ts):
    img = getImage(input_ts)
    
    #subtract background
    if not bgrd_size == 0:
         img = cv2.morphologyEx(img,cv2.MORPH_TOPHAT,disk(bgrd_size))
    
    #apply deconvolution
    img_dec = deconvlucy(img, psf, num_iter)
    
    img_dec = img_dec/scale_factor
    img_dec[img_dec > 65535] = 65535
    
    if not os.path.exists(dirout):
        os.makedirs(dirout)
    d = input_ts.to_dict()
    [head,tail] = os.path.split(d['mipmapLevels'][0]['imageUrl'])
    outImage = "%s/%s_%04d_%s"%(dirout, stackname, input_ts.z,tail)
    tifffile.imsave(outImage, np.uint16(img_dec))

    output_ts = input_ts
    d = output_ts.to_dict()
    for i in range(1,len(d['mipmapLevels'])):
        del d['mipmapLevels'][i]
    d['mipmapLevels'][0]['imageUrl'] = outImage
    output_ts.from_dict(d)
    return output_ts

class ApplyDeconv(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = ApplyDeconvParams
        super(ApplyDeconv,self).__init__(schema_type=schema_type,*args,**kwargs)

    def run(self):

        #get tilespecs
        Z = self.args['z_index']
        inp_tilespecs = renderapi.tilespec.get_tile_specs_from_z(
            self.args['input_stack'], Z, render=self.render)

        #deconvolve each tilespecs and return tilespecs
        #render=self.render
        psf = getPSF(self.args['psf_file'])

        mypartial = partial(process_tile, psf, self.args['num_iter'],
                            self.args['bgrd_size'], self.args['scale_factor'],
                            self.args['output_directory'], self.args['output_stack'])
        with renderapi.client.WithPool(self.args['pool_size']) as pool:
            tilespecs = pool.map(mypartial,inp_tilespecs)

        #upload to render
        renderapi.stack.create_stack(
                self.args['output_stack'],cycleNumber=2,cycleStepNumber=1,
                render=self.render)
        renderapi.client.import_tilespecs(
                self.args['output_stack'],tilespecs,render=self.render,
                close_stack=self.args['close_stack'])
#        renderapi.stack.set_stack_state(
#                self.args['output_stack'],"COMPLETE",render=self.render)

if __name__ == "__main__":
    mod = ApplyDeconv(input_data=example_input,schema_type=ApplyDeconvParams)
    mod.run()
