#!/usr/bin/env python
import renderapi
from renderapi.transform import AffineModel
import json
from ..module.render_module import RenderModule,RenderParameters
from pathos.multiprocessing import Pool
from functools import partial
import tempfile
import marshmallow as mm
import os
import cv2
import numpy as np

#An example set of parameters for this module
example_parameters = {
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":8080,
        "owner":"Forrest",
        "project":"M247514_Rorb_1",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    'input_stack':'ALIGNEM_reg2',
    'output_stack':'ALIGNEM_reg2_clahe',
    'pool_size':20
}
class FilterEMParameters(RenderParameters):
    input_stack = mm.fields.Str(required=True,metadata={'description':'stack to apply affine to'})
    output_stack = mm.fields.Str(required=False,metadata={'description':'stack to save answer into (defaults to overwriting input_stack)'})
    pool_size = mm.fields.Int(required=False,default=20,metadata={'description':'size of pool for parallel processing (default=20)'})
    sat_pix = mm.fields.Float(required=False,default=.2,metadata={'description':'percent of pixels to saturate when normalizing contrast (default .2%)'})
    contrast_adjust = mm.fields.Float(required=False,default=.85,metadata={'description':'constrast fraction to adjust before CLAHE (default .85)'})
    clahe_size = mm.fields.Int(required=False,default=90,metadata={'description':'CLAHE parameter for grid size.. smaller is less strong, larger is stronger (default 90)'})
    clahe_clip_limit = mm.fields.Float(required=False,default=1.5,metadata={'description':'clip limit for CLAHE normalization (default 1.5)'})
    vert_flip = mm.fields.Boolean(required=False,default=True,metadata={'description':'vertically flip the image (default True)'})
def fix_url(url):
    path = url.replace('file:','')
    path = path.replace('%20',' ')
    return path

class FilterEMModule(RenderModule):
    def __init__(self,*args,**kwargs):
        super(FilterEMModule,self).__init__(*args, **kwargs)


    def filter_em_image(self,path_in,path_out):

        img = cv2.imread(path_in,cv2.CV_8UC1)

        mask=np.array(img>0,np.uint8)
        img = 255-img
        #f, ax = plt.subplots(1,1,figsize=(10,10))
        #ax.imshow(img,cmap=plt.cm.gray)
        sat_pix = self.args['sat_pix']/100

        hgram=cv2.calcHist([img],[0],mask,[256],[0,256])
        cum_dist = np.cumsum(hgram)/np.sum(hgram)
        min_level = np.where(np.diff(cum_dist>sat_pix)==1)[0][0]
        max_level = np.where(np.diff(cum_dist<(1.0-sat_pix))==1)[0][0]

        img = np.array(img,np.double)
        if (max_level==min_level):
            print 'min_level',min_level
            print 'max_level',max_level
            print 'on file',path_in
            raise Exception("%s %f %f"%(path_in,min_level,max_level))

        img = ((img-min_level)/(max_level-min_level))*255
        img = (img - 128)*self.args['contrast_adjust'] + 128
        #print 'img[2012,195]',img[2012,195]
        img = np.clip(img,0,255)
        #print 'img[2012,195]',img[2012,195]
        img = np.array(img,np.uint8)
        #print 'img[2012,195]',img[2012,195]

        img = cv2.bilateralFilter(img,3,20,20)
        #clahe1 = cv2.createCLAHE(clipLimit=.5, tileGridSize=(10,10))
        grid_size = self.args['clahe_size']
        clahe2 = cv2.createCLAHE(clipLimit=self.args['clahe_clip_limit'],
            tileGridSize=(grid_size,grid_size))
        #img = clahe1.apply(img)
        img = clahe2.apply(img)
        if self.args['vert_flip']:
            img = cv2.flip(img,0)
        cv2.imwrite(path_out,img)

    def process_z(self,render,input_stack,z):

            #get the tilespecs for this Z
            tilespecs = render.run(renderapi.tilespec.get_tile_specs_from_z,input_stack,z)

            #loop over the tilespes adding the transform
            for ts in tilespecs:
                mml = ts.ip.mipMapLevels[0]

                old_url = mml.imageUrl
                old_path = fix_url(old_url)

                directory,old_file = os.path.split(old_path)

                #print 'old_file',old_file
                orig_tif = next(f for f in os.listdir(directory)
                    if ((old_file[0:-9] in f)) and ('flip' not in f) and ('mask' not in f) and (not f.endswith('bak0')))
                #print 'orig_tif',orig_tif
                orig_path = os.path.join(directory,orig_tif)

                new_url = mml.imageUrl[0:-4]+'_flip.tif'
                new_path = fix_url(new_url)

                self.filter_em_image(orig_path,new_path)

                mml.imageUrl = new_url
                ts.ip.update(mml)
            #open a temporary file
            tid,tfile = tempfile.mkstemp(suffix='.json')
            file = open(tfile,'w')
            #write the file to disk
            renderapi.utils.renderdump(tilespecs,file)
            os.close(tid)
            #return the filepath
            return tfile

    def run(self):
        #get the z values in the stack
        zvalues = self.render.run(renderapi.stack.get_z_values_for_stack,self.args['input_stack'])

        #output_stack defaults to input_stack
        output_stack = self.args.get('output_stack',self.args['input_stack'])

        #define a processing pool
        pool = Pool(self.args['pool_size'])

        #define a partial function for processing a single z value
        mypartial = partial(self.process_z,self.render,self.args['input_stack'])

        #mypartial(0)
        #get the filepaths of json files in parallel
        json_files = pool.map(mypartial,zvalues)

        if self.args['input_stack'] != output_stack:
            sv = renderapi.stack.get_stack_metadata(self.args['input_stack'],render=self.render)
            renderapi.stack.create_stack(output_stack,render=self.render)
            renderapi.stack.set_stack_metadata(output_stack,sv,render=self.render)
        #import the json_files into the output stack
        renderapi.client.import_jsonfiles_parallel(output_stack,
            json_files,
            poolsize=mod.args['pool_size'],
            render=self.render)

        #clean up the temp files
        [os.remove(tfile) for tfile in json_files]


if __name__ == '__main__':
    #process the command line arguments
    mod = FilterEMModule(schema_type=FilterEMParameters,input_data=example_parameters)
    mod.run()
