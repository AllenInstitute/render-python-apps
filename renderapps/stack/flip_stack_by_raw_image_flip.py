#!/usr/bin/env python
import renderapi
from renderapi.transform import AffineModel
from ..module.render_module import RenderModule, RenderParameters
import os
from functools import partial
import subprocess
import tempfile
from argschema.fields import Str, Int, Boolean

# An example set of parameters for this module
example_parameters = {
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":8080,
        "owner":"Forrest",
        "project":"M247514_Rorb_1",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    'input_stack':'ACQDAPI_1',
    'output_stack':'ACQDAPI_1_junkflip3',
    'minZ':0,
    'maxZ':0,
    'delete_after':False
}

class FlipStackParameters(RenderParameters):
    input_stack = Str(required=True,description='stack to apply affine to')
    output_stack = Str(required=False,description='stack to save answer into (defaults to overwriting input_stack)')
    minZ = Int(required=True,description='minimum Z to flip')
    maxZ = Int(required=True,description='maximum Z to flip')
    pool_size = Int(required=False,default=20,description='size of pool for parallel processing (default=20)')
    delete_after = Boolean(required=False,default=False,description='whether to delete the old image files or not after flipping')

def fix_url(url):
    path = url.replace('file:','')
    path = path.replace('%20',' ')
    return path

#define a function to process one z value
def process_z(render,input_stack,z,delete_after=False):
    #get the tilespecs for this Z
    tilespecs = render.run(renderapi.tilespec.get_tile_specs_from_z,input_stack,z)
    #loop over the tilespes adding the transform
    for ts in tilespecs:
        #slide this tile up according to its minimumX
        slide_up = AffineModel(B1=-2*ts.minY)
        ts.tforms.append(slide_up)

        #get the old minimum mipmaplevel
        mml = ts.ip.mipMapLevels[0]
        old_url = mml.imageUrl
        old_path = fix_url(old_url)

        new_url = mml.imageUrl[0:-4]+'_flip.png'
        new_path = fix_url(new_url)

        #construct the imagemagick command
        cmd = ['convert',old_path,'-flip',new_path]
        mml.imageUrl = new_url
        ts.ip.update(mml)

        #execute the imagemagick subprocess
        proc = subprocess.Popen(cmd)
        proc.wait()

        if delete_after:
            #remove me to delete
            os.remove(old_path)

    #open a temporary file
    tid,tfile = tempfile.mkstemp(suffix='.json')
    file = open(tfile,'w')
    #write the file to disk
    renderapi.utils.renderdump(tilespecs,file)
    os.close(tid)

    #return the filepath
    return tfile

class FlipStack(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = FlipStackParameters
        super(FlipStack,self).__init__(schema_type=schema_type,*args,**kwargs)
    def run(self):
        self.logger.debug(self.args)
        self.logger.error('WARNING NEEDS TO BE TESTED, TALK TO FORREST IF BROKEN')

        #get the z values in the stack
        zvalues = range(mod.args['minZ'],mod.args['maxZ']+1)

        #output_stack defaults to input_stack
        output_stack = mod.args.get('output_stack',mod.args['input_stack'])

        #define a partial function for processing a single z value
        mypartial = partial(process_z,mod.render,mod.args['input_stack'],delete_after=mod.args['delete_after'])

        #mypartial(0)
        #get the filepaths of json files in parallel
        with renderapi.client.WithPool(self.args['pool_size']) as pool:
            json_files = pool.map(mypartial,zvalues)

        if mod.args['input_stack']!=output_stack:
            renderapi.stack.create_stack(output_stack,render=mod.render)

        #import the json_files into the output stack
        renderapi.client.import_jsonfiles_parallel(output_stack,json_files,poolsize=mod.args['pool_size'],render=mod.render)

        #clean up the temp files
        [os.remove(tfile) for tfile in json_files]

if __name__ == "__main__":
    mod = FlipStack(input_data= example_parameters)
    mod.run()
