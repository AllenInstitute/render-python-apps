import argparse
import json
import os
import pandas as pd
import subprocess
import copy
import renderapi
from renderapi.tilespec import TileSpec,Layout,MipMapLevel
from renderapi.transform import AffineModel

my_env = os.environ.copy()
from itertools import izip_longest



def make_tilespec_from_statetable (df,rootdir,outputProject,outputOwner,minval=0,maxval=50000):
    df = df[df['zstack']==0]
    #ribbons = df.groupby('ribbon')
    #zoffset=0

    #for ribbnum,ribbon in ribbons:
    #    ribbon.loc[ribbon.index,'z']=ribbon['section']+zoffset
    #    zoffset += ribbon['section'].max()+1
    #    df.loc[ribbon.index,'z']=ribbon['z'].values


    cmds = []
    tilespecpaths = []
    for ((ch,sess),chgroup) in df.groupby(['ch_name','session']):
        print ch,sess
    
        for ((rib,sect),group) in chgroup.groupby(['ribbon','section']):
            tilespeclist=[]
            z=0
            for ind,row in group.iterrows():
                filepath=row.full_path
                fileparts=filepath.split(os.path.sep)[1:]
                tilespecdir = rootdir + "/processed/downsamp_tilespec/"+fileparts[5]+"/"+fileparts[6]+"/"+fileparts[7]
                #print tilespecdir
                if not os.path.isdir(tilespecdir):
                    os.makedirs(tilespecdir)
                downdir = rootdir+"/processed/downsamp_images/"+fileparts[5]+"/"+fileparts[6]+"/"+fileparts[7]
                #print "This is the Down Sampled Directory: %s"%downdir

                if not os.path.exists(downdir):
                    os.makedirs(downdir)
               
                        #construct command for creating mipmaps for this tilespec
                downcmd = ['python','create_mipmaps.py','--inputImage',filepath,'--outputDirectory',downdir,'--mipmaplevels','1','2','3']
                cmds.append(downcmd)
                layout = Layout(sectionId=row.ribbon*1000+row.section,
                                                scopeId='Leica',
                                                cameraId='zyla',
                                                imageRow=0,
                                                imageCol=0,
                                                stageX = row.xstage,
                                                stageY = row.ystage,
                                                rotation = 0.0,
                                                pixelsize = row.scale_x)
                
                mipmap0 = MipMapLevel(level=0,imageUrl=row.full_path)
                mipmaplevels=[mipmap0]
                filename = "%s_S%04d_F%04d_Z%02d.tif"%(row.ch_name,row.section,row.frame,0)
                for i in range(1,4):
                    scUrl = 'file:' + os.path.join(downdir,filename[0:-4]+'_mip0%d.jpg'%i)
                    mml = MipMapLevel(level=i,imageUrl=scUrl)
                    mipmaplevels.append(mml)

                tform = AffineModel(M00=row.a00,
                                         M01=row.a01,
                                         M10=row.a10,
                                         M11=row.a11,
                                         B0=row.a02,
                                         B1=row.a12)
            
                tilespeclist.append(TileSpec(tileId=row.tileID,
                                     frameId = row.frame,
                                     z=row.z,
                                     width=row.width,
                                     height=row.height,
                                     mipMapLevels=mipmaplevels,
                                     tforms=[tform],
                                     minint=minval,
                                     maxint=maxval,
                                     layout= layout))
                z = row.z
        
            json_text=json.dumps([t.to_dict() for t in tilespeclist],indent=4)
            json_file = os.path.join(tilespecdir,outputProject+'_'+outputOwner+'_'+outputStack+'_%04d.json'%z)
            fd=open(json_file, "w")
            fd.write(json_text)
            fd.close()
            tilespecpaths.append(json_file)
    return tilespecpaths,cmds






if __name__ == "__main__":


    DEFAULT_HOST = "ibs-forrestc-ux1"
    DEFAULT_PORT = 8080
    DEFAULT_OWNER = "Forrest"
    DEFAULT_PROJECT = "TEST"
    DEFAULT_CLIENT_SCRIPTS = '/pipeline/render/render-ws-java-client/src/main/scripts'
    parser = argparse.ArgumentParser(description="Create fast Stacks")
    parser.add_argument('--statetableFile', help="State Table File")
    parser.add_argument('--projectDirectory',        help="name of the input Project")
    parser.add_argument('--outputStackPrefix', help = "Output Stack Prefix")
    parser.add_argument('--owner',default=DEFAULT_OWNER,required=False)
    parser.add_argument('--project',default=DEFAULT_PROJECT,required=False)
    parser.add_argument('--host',default=DEFAULT_HOST,required=False)
    parser.add_argument('--port',default=8080,required=False)
    parser.add_argument('--client_scripts',default=DEFAULT_CLIENT_SCRIPTS,required=False,type=str,help='default client location')
    args = parser.parse_args()

    outputProject=args.project
    outputOwner = args.owner
    statetablefile = args.statetableFile
    rootdir = args.projectDirectory

    df = pd.read_csv(statetablefile)
    ribbons = df.groupby('ribbon')  
    r = renderapi.render.connect(**vars(args))
    k=0
    for ribnum,ribbon in ribbons:
        mydf = ribbon.groupby('ch_name')
        for channum,chan in mydf:
            outputStack = args.outputStackPrefix + '_%s'%(channum)
            
            print "creating tilespecs and cmds...."
            tilespecpaths,cmds = make_tilespec_from_statetable (chan,rootdir,outputProject,outputOwner)
            print "importing tilespecs into render...."
            print "creating downsampled images ..."
            groups = [(subprocess.Popen(cmd, stdout=subprocess.PIPE) for cmd in cmds)] * 20 # itertools' grouper recipe
            for processes in izip_longest(*groups): # run len(processes) == limit at a time
               for p in filter(None, processes):
                   p.wait()
            print "uploading to render ..."
            if k==0:
                renderapi.stack.create_stack(outputStack,owner=outputOwner,project=outputProject,verbose=False,render=r)
            print tilespecpaths
            renderapi.client.import_jsonfiles_parallel(outputStack,tilespecpaths,render=r)
        k+=1
            
