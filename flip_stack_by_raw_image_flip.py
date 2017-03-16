#!/usr/bin/env python
import renderapi 
from renderapi.tilespec import MipMapLevel
from renderapi.transform import AffineModel
import json
from render_module import RenderModule,RenderParameters
from pathos.multiprocessing import Pool
from functools import partial
import subprocess
import tempfile
import marshmallow as mm
import os
#An example set of parameters for this module
example_parameters = {
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":8080,
        "owner":"Forrest",
        "project":"M247514_Rorb_1",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    'input_stack':'EM_Site4_stitched',
    'output_stack':'EM_Site4_stitched',
    'minZ':0,
    'maxZ':0,
    'delete_after':False
}

class FlipStackParameters(RenderParameters):
    input_stack = mm.fields.Str(required=True,metadata={'description':'stack to apply affine to'})
    output_stack = mm.fields.Str(required=False,metadata={'description':'stack to save answer into (defaults to overwriting input_stack)'})
    minZ = mm.fields.Int(required=False,metadata={'description':'minimum Z to flip'})
    maxZ = mm.fields.Int(required=False,metadata={'description':'maximum Z to flip'})
    pool_size = mm.fields.Int(required=False,default=20,metadata={'description':'size of pool for parallel processing (default=20)'})
    delete_after = mm.fields.Boolean(required=False,default=False,metadata={'description':'whether to delete the old image files or not after flipping'})

if __name__ == '__main__':
    #process the command line arguments
    mod = RenderModule(schema_type=FlipStackParameters,input_data=example_parameters)
    #mod.run()
    #get the z values in the stack
    zvalues = mod.render.run(renderapi.stack.get_z_values_for_stack,mod.args['input_stack'])

    #define a function to process one z value
    def process_z(render,input_stack,z,delete_after=False):
        #get the tilespecs for this Z
        tilespecs = render.run(renderapi.tilespec.get_tile_specs_from_z,input_stack,z)
        #loop over the tilespes adding the transform
        for ts in tilespecs:
            #slide this tile up according to its minimumX
            slide_up = AffineModel(B1=-ts.minX)
            ts.tforms.append(slide_up)

            #get the old minimum mipmaplevel
            mml = ts.ip.mipMapLevels[0]
            old_url = mml.imageUrl
            new_url = os.path.splitext(mml.imageUrl)[1]+'_flip.tif'
            #construct the imagemagick command
            cmd = ['convert',mml.imageUrl,'_flip',new_url]
            mml.imageUrl = new_url
            ts.ip.update(mml)
            
            #execute the imagemagick subprocess
            proc = subprocess.Popen(cmd)
            proc.wait()

            if delete_after:
                #remove me to delete
                os.remove(old_url)

        #open a temporary file
        tid,tfile = tempfile.mkstemp(suffix='.json')
        file = open(tfile,'w')
        #write the file to disk
        renderapi.utils.renderdump(tilespecs,file)
        os.close(tid)

        #return the filepath
        return tfile

    #output_stack defaults to input_stack
    output_stack = mod.args.get('output_stack',mod.args['input_stack'])

    #define a processing pool
    pool = Pool(mod.args['pool_size'])
    #define a partial function for processing a single z value
    mypartial = partial(process_z,mod.render,mod.args['input_stack'],global_tform,delete_after=mod.args['delete_after'])

    #get the filepaths of json files in parallel
    json_files = pool.map(mypartial,zvalues)
    #import the json_files into the output stack
    renderapi.client.import_jsonfiles_parallel(output_stack,json_files,poolsize=mod.args['pool_size'],render=mod.render)

    #clean up the temp files
    [os.remove(tfile) for tfile in json_files]