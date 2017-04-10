import json
import os
from create_mipmaps import create_mipmaps
import renderapi
from renderapi.tilespec import MipMapLevel
import argparse
from pathos.multiprocessing import Pool
from functools import partial

def make_tilespecs_and_cmds(render,inputStack,outputStack,tilespecdir):
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
            tilespecdir = os.path.join(os.path.sep,
                                       fileparts[0], 
                                       fileparts[1],
                                       fileparts[2],
                                       'processed',
                                       tilespecdir)
            if not os.path.isdir(tilespecdir):
                os.makedirs(tilespecdir)
            if not os.path.isdir(downdir):
                os.makedirs(downdir)
         
            filebase,filename = os.path.split(filepath)
            downdir2 = downdir.replace(" ","%20")
            for i in range(1,4):
                scUrl = 'file:' + os.path.join(downdir2,filename[0:-4]+'_mip0%d.jpg'%i)
                mml = MipMapLevel(level=i,imageUrl=scUrl)
                tilespec.ip.update(mml)

           
        tilespecpath = os.path.join(tilespecdir,outputStack+'_%04d.json'%z)
        fp = open(tilespecpath,'w')
        renderapi.utils.renderdump(tilespecs,fp,indent=4)
        fp.close()
        tilespecpaths.append(tilespecpath)
    return tilespecpaths,mipmap_args

def create_mipmap_from_tuple(mipmap_tuple,convertTo8Bit=True):
    (filepath,downdir)=mipmap_tuple
    return create_mipmaps(filepath,downdir,convertTo8Bit=convertTo8Bit) 

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Take an existing render stack, and create a new render stack with downsampled tilespecs and create those downsampled tiles")

    parser.add_argument('--renderHost',help="host name of the render server",default="ibs-forrestc-ux1")
    parser.add_argument('--renderPort',help="port of the render server",default = 8080)
    parser.add_argument('--inputOwner',help="name of project owner to read project from",default = "Forrest")
    parser.add_argument('--inputProject',help="name of the input Project",required=True)
    parser.add_argument('--inputStack',help='name of stack to take in',required=True)
    parser.add_argument('--outputStack',help='name of stack to upload to render',required=True) 
    parser.add_argument('--outputTileSpecDir',help='location to save tilespecs before uploading to render (default to ',default='tilespec_downsampled')
    parser.add_argument('--client_scripts',help='path to render client scripts',default='/pipeline/render/render-ws-java-client/src/main/scripts')
    parser.add_argument('--ndvizBase',help="base url for ndviz surface",default="http://ibs-forrestc-ux1:8000/render/172.17.0.1:8081")
    parser.add_argument('--do_not_convert', dest='convertTo8Bit', action='store_false')
    parser.add_argument('--verbose',help="verbose output",default=False)
    parser.set_defaults(convertTo8Bit=True)
    args = parser.parse_args()

    render = renderapi.render.connect(host=args.renderHost,
                                      port=args.renderPort,
                                      owner=args.inputOwner,
                                      project=args.inputProject,
                                      client_scripts = args.client_scripts)

    render.run(renderapi.stack.delete_stack,args.outputStack)
    print ""
    #create a new stack to upload to render
    render.run(renderapi.stack.create_stack,args.outputStack)

    #go get the existing input tilespecs, make new tilespecs with downsampled URLS, save them to the tilespecpaths, and make a list of commands to make downsampled images
    tilespecpaths,mipmap_args = make_tilespecs_and_cmds(render,args.inputStack,args.outputStack,args.outputTileSpecDir)
   
    #upload created tilespecs to render
    render.run(renderapi.client.import_jsonfiles_parallel,
               args.outputStack,
               tilespecpaths)
   
    print "making downsample images"
    print "conversion ",args.convertTo8Bit
    pool = Pool(30)
    mypartial = partial(create_mipmap_from_tuple,convertTo8Bit=args.convertTo8Bit)
    results=pool.map(mypartial,mipmap_args)


    print "finished!"

