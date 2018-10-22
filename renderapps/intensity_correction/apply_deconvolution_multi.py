if __name__ == "__main__" and __package__ is None:
    __package__ = "renderapps.intensity_correction.apply_deconvolution"
import os
import renderapi
from ..module.render_module import RenderModule, RenderParameters
from argschema.fields import InputFile, InputDir, Str, Float, Int, Bool, Nested
from argschema.schemas import DefaultSchema
from functools import partial
import numpy as np
from skimage.morphology import disk
import cv2
import tifffile
from deconvtools import deconvlucy

example_input = {
    'render': {
        'host': '10.128.24.33',
        'port': 80,
        'owner': 'multchan',
        'project': 'M335503_Ai139_smallvol',
        'client_scripts': '/shared/render/render-ws-java-client/src/main/scripts'
    },
    "input_stack": "FF_Session1",
    "output_stack": "TEST_DCV_Session1",
    "output_directory": "/nas2/data/M335503_Ai139_smallvol/processed/TESTDeconvolved",
    "z_index": 500,
    "pool_size": 24,
    "deconv_settings": [
        {
            "name": "DAPI_1",
            "num_iter": 20,
            "scale_factor": 2,
            "bgrd_size": 20,
            "psf_file": "/nas2/data/M335503_Ai139_smallvol/processed/psfs/psf_DAPI.tif"
        },
        {
            "name": "PSD95",
            "num_iter": 20,
            "scale_factor": 4,
            "bgrd_size": 20,
            "psf_file": "/nas2/data/M335503_Ai139_smallvol/processed/psfs/psf_PSD95.tif"
        },
        {
            "name": "GFP",
            "num_iter": 20,
            "scale_factor": 5,
            "bgrd_size": 50,
            "psf_file": "/nas2/data/M335503_Ai139_smallvol/processed/psfs/psf_GFP.tif"
        },
        {
            "name": "Gephyrin",
            "num_iter": 20,
            "scale_factor": 4,
            "bgrd_size": 20,
            "psf_file": "/nas2/data/M335503_Ai139_smallvol/processed/psfs/psf_Gephyrin.tif"
        }
    ]
}


class ChannelDeconvSettings(DefaultSchema):
    name = Str(required=False,
               default="",
               description="name of channel to apply setting (blank string for default channel)")
    psf_file = InputFile(required=True,
                         description='path to psf file')
    bgrd_size = Int(required=False, default=20,
                    description='size of rolling ball (default=20)')
    num_iter = Int(required=True, default=20,
                   description='number of iterations (default=20)')
    scale_factor = Int(required=False, default=1,
                       description='scaling factor (default=1)')


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
    deconv_settings = Nested(ChannelDeconvSettings,
                             many=True,
                             description="channel specific deconvolution settings")
    close_stack = Bool(required=False, default=False,
                       description="whether to close stack or not")

def getBaseUrl(ts, chan=None):
    if chan is None:
        url = ts.ip[0].imageUrl
    else:
        chan = next(ch for ch in ts.channels if ch.name == chan)
        url =chan.ip[0].imageUrl
    
    return url

def getImage(ts, chan=None):
    url = getBaseUrl(ts, chan)
    img = tifffile.imread(url)

    img = img.astype(float)
    return img


def getPSF(filename):
    psf = tifffile.imread(filename)
    psf = psf.astype(float)
    psf = psf/np.sum(psf)
    return psf

# def subtract_bgrd(img, bgrd_size):
#     if not bgrd_size == 0:
#         img = cv2.morphologyEx(img,cv2.MORPH_TOPHAT,disk(bgrd_size))


def process_tile(psf, num_iter, bgrd_size, scale_factor, dirout, stackname, input_ts, chan=None):
    img = getImage(input_ts, chan)

    # subtract background
    if not bgrd_size == 0:
        img = cv2.morphologyEx(img, cv2.MORPH_TOPHAT, disk(bgrd_size))

    # apply deconvolution
    img_dec = deconvlucy(img, psf, num_iter)

    img_dec = img_dec/scale_factor
    img_dec[img_dec > 65535] = 65535

    if not os.path.exists(dirout):
        os.makedirs(dirout)
    imageUrl = getBaseUrl(input_ts, chan)
    [head, tail] = os.path.split(imageUrl)
    outImage = "%s/%s_%04d_%s" % (dirout, stackname, input_ts.z, tail)
    tifffile.imsave(outImage, np.uint16(img_dec))

    return outImage


def process_multichannel_tile(psf_dict, chan_settings, dirout, stackname, input_ts):
    def_chan = next(ch.name for ch in input_ts.channels if ch.ip[0].imageUrl == input_ts.ip[0].imageUrl)
    for chan in input_ts.channels:
        chan_d = next(chd for chd in chan_settings if chd['name']==chan.name)
        imageUrl = chan.ip[0].imageUrl
        deconvUrl = process_tile(psf_dict[chan.name],
                                 chan_d['num_iter'],
                                 chan_d['bgrd_size'],
                                 chan_d['scale_factor'],
                                 dirout,
                                 stackname,
                                 input_ts,
                                 chan = chan.name)
        chan.ip = renderapi.image_pyramid.ImagePyramid()
        chan.ip[0] = renderapi.image_pyramid.MipMap(imageUrl = deconvUrl)
    input_ts.ip = next(chan.ip for chan in input_ts.channels if chan.name == def_chan)
    return input_ts

class ApplyDeconv(RenderModule):
    default_schema = ApplyDeconvParams

    def run(self):

        # get tilespecs
        Z = self.args['z_index']
        inp_tilespecs = renderapi.tilespec.get_tile_specs_from_z(
            self.args['input_stack'], Z, render=self.render)

        # deconvolve each tilespecs and return tilespecs
        # render=self.render
        psf_dict = {}
        for chan_settings in self.args['deconv_settings']:
            psf_dict[chan_settings['name']] = getPSF(
                chan_settings['psf_file'])

        mypartial = partial(process_multichannel_tile,
                            psf_dict,
                            self.args['deconv_settings'],
                            self.args['output_directory'],
                            self.args['output_stack'])
        with renderapi.client.WithPool(self.args['pool_size']) as pool:
            tilespecs = pool.map(mypartial, inp_tilespecs)
        
        # upload to render
        renderapi.stack.create_stack(
            self.args['output_stack'], cycleNumber=2, cycleStepNumber=2,
            render=self.render)
        renderapi.client.import_tilespecs(
            self.args['output_stack'], tilespecs, render=self.render,
            close_stack=self.args['close_stack'])
#        renderapi.stack.set_stack_state(
#                self.args['output_stack'],"COMPLETE",render=self.render)


if __name__ == "__main__":
    mod = ApplyDeconv(input_data=example_input, schema_type=ApplyDeconvParams)
    mod.run()
