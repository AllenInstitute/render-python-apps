import json
import os
from create_mipmaps import create_mipmaps
import renderapi
from renderapi.tilespec import MipMapLevel
import argparse
from functools import partial
from pathos.multiprocessing import Pool
from ..module.render_module import RenderModule, RenderParameters
import marshmallow as mm
import tempfile

example_json={
        "render":{
            "host":"ibs-forrestc-ux1",
            "port":8080,
            "owner":"Forrest",
            "project":"M247514_Rorb_1",
            "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
        },
        "input_stack":"BIGALIGN2_MARCH24c_EM_clahe",
        "output_stack":"BIGALIGN2_MARCH24c_EM_clahe_mm",
        "convert_to_8bit":True
}

class AddDownSampleParameters(RenderParameters):
    input_stack = mm.fields.Str(required=True,
        metadata={'description':'stack to input'})
    output_stack = mm.fields.Str(required=True,
        metadata={'description':'stack to output (deletes before upload)'})
    convert_to_8bit = mm.fields.Boolean(required=False,default=True,
        metadata={'description':'convert the data from 16 to 8 bit (default True)'})
    pool_size = mm.fields.Int(required=False, default=20,
        metadata={'description':'size of parallelism'})

def make_tilespecs_and_cmds(render,inputStack,outputStack):
    zvalues=render.run(renderapi.stack.get_z_values_for_stack,inputStack)
    mipmap_args = []
    tilespecpaths=[]
    for z in zvalues:
        tilespecs = render.run(renderapi.tilespec.get_tile_specs_from_z,inputStack,z)
        
        for i,tilespec in enumerate(tilespecs):
            mml = tilespec.ip.mipMapLevels[0]

            old_url = mml.imageUrl
            filepath=str(old_url).lstrip('file:')
            filepath=filepath.replace("%20"," ")
            fileparts=filepath.split(os.path.sep)[1:]
            downdir=os.path.join(os.path.sep,
                              fileparts[0],
                              fileparts[1],
                              fileparts[2],
                              'processed',
                              'downsampled_images',
                              fileparts[5],
                              fileparts[6],
                              fileparts[7])
            #construct command for creating mipmaps for this tilespec
            mipmap_args.append((filepath,downdir))

            filebase, filename = os.path.split(filepath)
            downdir2 = downdir.replace(" ", "%20")
            for i in range(1, 4):
                scUrl = 'file:' + os.path.join(downdir2,filename[0:-4]+'_mip0%d.jpg'%i)
                mml = MipMapLevel(level=i,imageUrl=scUrl)
                tilespec.ip.update(mml)
      
        tempjson = tempfile.NamedTemporaryFile(
            suffix=".json", mode='r', delete=False)
        tempjson.close()
        tsjson = tempjson.name
        with open(tsjson, 'w') as f:
            renderapi.utils.renderdump(tilespecs, f)
            f.close()
        tilespecpaths.append(tsjson)

  
    return tilespecpaths,mipmap_args

def create_mipmap_from_tuple(mipmap_tuple,convertTo8Bit=True):
    (filepath,downdir)=mipmap_tuple
    return create_mipmaps(filepath,downdir,convertTo8Bit=convertTo8Bit) 

class AddDownSample(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = AddDownSampleParameters
        super(AddDownSample,self).__init__(schema_type=schema_type,*args,**kwargs)
    def run(self):
        self.logger.error('WARNING NEEDS TO BE TESTED, TALK TO FORREST IF BROKEN')

        self.render.run(renderapi.stack.delete_stack,self.args['output_stack'])

        #create a new stack to upload to render
        self.render.run(renderapi.stack.create_stack,self.args['output_stack'])

        #go get the existing input tilespecs, make new tilespecs with downsampled URLS, save them to the tilespecpaths, and make a list of commands to make downsampled images
        tilespecpaths,mipmap_args = make_tilespecs_and_cmds(self.render,
                                                            self.args['input_stack'],
                                                            self.args['output_stack'])
    
        #upload created tilespecs to render
        self.render.run(renderapi.client.import_jsonfiles_parallel,
                self.args['output_stack'],
                tilespecpaths)
    
        self.logger.debug("making downsample images")
        self.logger.debug("convert_to_8bit:{}".format(self.args['convert_to_8bit']))
        pool = Pool(self.args['pool_size'])
        mypartial = partial(create_mipmap_from_tuple,convertTo8Bit=self.args['convert_to_8bit'])
        results=pool.map(mypartial,mipmap_args)

if __name__ == "__main__":
    mod = AddDownSample(input_data= example_json)
    mod.run()


