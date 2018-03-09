if __name__ == "__main__" and __package__ is None:
    __package__ = "renderapps.intensity_correction.apply_deconv_zoned"
import os
import renderapi
from ..module.render_module import RenderModule, RenderParameters
from argschema.fields import InputFile, InputDir, Str, Float, Int, Bool
from functools import partial
import numpy as np
from skimage.morphology import disk
import cv2
import tifffile
from deconvtools import deconvlucy, deconvblind

example_input = {
    "render": {
        "host": "ibs-forrestc-ux1",
        "port": 8080,
        "owner": "Forrest",
        "project": "M246930_Scnn1a_4_f1",
        "client_scripts": "/var/www/render/render-ws-java-client/src/main/scripts"
    },
    "input_stack": "Flatfieldcorrected_3_Synapsin",
    "output_stack": "Deconv_zoned_3_Synapsin",
    "output_directory": "/nas/data/M246930_Scnn1a_4_f1/processed/Deconv_zoned",
    "z_index": 0,
    "pool_size": 20,
    "psf_file": "/nas/data/M246930_Scnn1a_4_f1/processed/psfs/psf_Synapsin.tif",
    "num_iter": 20,
    "bgrd_size": 20,
    "scale_factor": 4
}

class ApplyDeconvZonedParams(RenderParameters):
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

def bloc_deconv(img, psf, num_iter, blocksize=[128,128], blockoverlap=[10,10], 
                   deconv='lucy'):
    print 'blocksize {}, blockoverlap {}, deconv {}, num iter {}'\
           .format(blocksize, blockoverlap, deconv, num_iter)    
    imgsize = img.shape    
    
    # calculate number of blocks    
    num_blocks = int((imgsize[0] + blocksize[0])/blocksize[0]*(imgsize[1] 
                      + blocksize[1])/blocksize[1])
    b0 = range(0, imgsize[0] + blocksize[0], blocksize[0])         
    b1 = range(0, imgsize[1] + blocksize[1], blocksize[1])    
    
    # divide image into blocks    
    blocks, idx = create_blocks(img, imgsize, num_blocks, b0, b1, blocksize, blockoverlap)
    
    # apply deconvolution to each block
    blocks_dec = []    
    if deconv == 'lucy':     
        psf_calc = []        
        if len(psf.shape) > 2:
            for k in range(num_blocks):
                blocks_dec.append(deconvlucy(blocks[k], psf[k,:,:], num_iter))
        else:
            for k in range(num_blocks):
                blocks_dec.append(deconvlucy(blocks[k], psf, num_iter))
    else:
        psf_init = np.ones((21,21))
        psf_calc = np.zeros((num_blocks, psf_init.shape[0], psf_init.shape[1]))        
        for k in range(num_blocks):
            blocks_dec_k, psf_calc[k,:,:] = deconvblind(blocks[k], psf_init, num_iter)
            blocks_dec.append(blocks_dec_k)
    
    # put blocks back together using average blending    
    img_dec = deblock(blocks_dec, imgsize, blocksize, num_blocks, b0, b1, blockoverlap, idx) 
    return img_dec, psf_calc

def create_blocks(img, imgsize, num_blocks, b0, b1, blocksize, blockoverlap):
    #divide image into blocks   
    # create block indices    
    idx = np.zeros((num_blocks,4), dtype=np.int)
    k = 0
    for n in b1:
        for m in b0: 
            idx[k, 0] = m - m/blocksize[0]*blockoverlap[0] # block's top edge
            idx[k, 1] = m - m/blocksize[0]*blockoverlap[0] + blocksize[0] #block's bottom edge
            idx[k, 2] = n - n/blocksize[1]*blockoverlap[1] # block's left edge
            idx[k, 3] = n - n/blocksize[1]*blockoverlap[1] + blocksize[1] # block's right edge
            if m == imgsize[0]:
                idx[k, 1] = m #block's bottom edge
            if n == imgsize[1]:
                idx[k, 3] = n #block's bottom edge
            k = k + 1 
                      
    #create blocks    
    blocks = []    
    for k in range(num_blocks):
        blocks.append(img[idx[k,0]:idx[k,1], idx[k,2]:idx[k,3]])
    return blocks, idx                 

def deblock(blocks, imgsize, blocksize, num_blocks, b0, b1, blockoverlap, idx):    
    # put blocks back together using average blending   
    mask = np.ones(imgsize)  
    #take into account masked 3 edge pixels on each block
    for m in b0[1:]:
        mask[m - m/blocksize[0]*blockoverlap[0] + 3:m - m/blocksize[0]*blockoverlap[0] 
             + blockoverlap[0] - 3, :] = 0.5  
    for n in b1[1:]:
        mask[:, n - n/blocksize[1]*blockoverlap[1] + 3:n - n/blocksize[1]*blockoverlap[1] 
             + blockoverlap[1] - 3] = 0.5
        for m in b0[1:]: 
            mask[m - m/blocksize[0]*blockoverlap[0] + 3:m - m/blocksize[0]*blockoverlap[0] 
             + blockoverlap[0] - 3, 
                 n - n/blocksize[1]*blockoverlap[1] + 3:n - n/blocksize[1]*blockoverlap[1] 
             + blockoverlap[1] - 3] = 0.25       
    #mask 3 edge pixels on each block except image borders
    for k in range(num_blocks):
       if idx[k,0]!=0:
           blocks[k][0:3,:] = 0
       if idx[k,1]!=imgsize[0]:
           blocks[k][-3:,:] = 0
       if idx[k,2]!=0:
           blocks[k][:,0:3] = 0 
       if idx[k,3]!=imgsize[1]:
           blocks[k][:,-3:] = 0
    img_new = np.zeros(imgsize)    
    for k in range(num_blocks):    
        img_new[idx[k,0]:idx[k,1], idx[k,2]:idx[k,3]]=\
        img_new[idx[k,0]:idx[k,1], idx[k,2]:idx[k,3]]+\
        blocks[k]*mask[idx[k,0]:idx[k,1], idx[k,2]:idx[k,3]]                        
    return img_new

def process_tile(num_iter, bgrd_size, scale_factor, dirout, stackname, input_ts):
    img = getImage(input_ts)
    
    #subtract background
    if bgrd_size == 50:
        img1 = cv2.morphologyEx(img,cv2.MORPH_TOPHAT,disk(bgrd_size)) 
    
    if not bgrd_size == 0:
        img = cv2.morphologyEx(img,cv2.MORPH_TOPHAT,disk(20))
    
    #apply deconvolution
    img_dec, psf_calc = bloc_deconv(img, psf=None, num_iter=10, blocksize=[128,128],
                                       blockoverlap=[10,10], deconv='blind')
    if bgrd_size == 50:
        img = img1
    
    img_dec, psf_calc = bloc_deconv(img, psf_calc, num_iter, blocksize=[128,128], 
                                       blockoverlap=[10,10], deconv='lucy')
    
    img_dec = img_dec/scale_factor
    img_dec[img_dec > 65535] = 65535
    
#    if not os.path.exists(dirout):
#        os.makedirs(dirout)
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

class ApplyDeconvZoned(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = ApplyDeconvZonedParams
        super(ApplyDeconvZoned,self).__init__(schema_type=schema_type,*args,**kwargs)

    def run(self):

        #get tilespecs
        Z = self.args['z_index']
        inp_tilespecs = renderapi.tilespec.get_tile_specs_from_z(
            self.args['input_stack'], Z, render=self.render)

        if not os.path.exists(self.args['output_directory']):
            os.makedirs(self.args['output_directory'])
        #deconvolve each tilespecs and return tilespecs
        #render=self.render
        #psf = getPSF(self.args['psf_file'])

        mypartial = partial(process_tile, self.args['num_iter'],
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
    mod = ApplyDeconvZoned(input_data=example_input,schema_type=ApplyDeconvZonedParams)
    mod.run()
