import renderapi
import matplotlib as mpl
mpl.use('Agg')
from renderapps.module.render_module import RenderParameters, RenderModule
import argschema
from renderapps.TrakEM2.AnnotationJsonSchema import AnnotationFile
import matplotlib.pyplot as plt
#%matplotlib notebook
import numpy as np
import os
import pandas as pd
from multiprocessing import pool
from functools import partial
import json


############## this is modified from notebook: http://ibs-forrestc-ux1:8888/notebooks/MakeSynaptogramsFromAnnotations.ipynb #####


example_parameters = {
    "render":{
        "host": "ibs-forrestc-ux1",
        "port": 80,
        "owner": "Forrest",
        "project": "M246930_Scnn1a_4_f1",
        "client_scripts": "/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    
    "global_annotation_file":"/nas/data/M246930_Scnn1a_4_f1/annotation/m246930_site5_annotation_MN_adjustZ_bb_Take2Site5_EMA_global.json",
    "annotation_metadata_json":"/nas/data/M246930_Scnn1a_4_f1/SEMdata/processed/Synaptograms/annotationMetadata/m246930_Take2Site5_synaptogram_metadata.json",
    "fig_directory":"/nas/data/M246930_Scnn1a_4_f1/SEMdata/processed/Synaptograms/Take2Site5_TdTeSyn",
    "synapses_to_make":['1226','1326','1416','2171','2299','668','2707','2709','2711'],   
    "channel_stacks":[
                     {
 
                            "stack":"EMSite5_take2_EMA"
                        },
                        {

                            "stack":"EMSite5_take2_EMA"
                        },
                        {
                            "channel":"TdTomato",
                            "stack":"Take2Site5_EMA_STI_DCV_FF_allSession_2",
                            "maxIntensity":10000
                        },
                        {
                            "channel":"synapsin",
                            "stack":"Take2Site5_manReg_EMA_STI_DCV_FF_allSession_3",
                            "maxIntensity":16000
                        }
                    ]
}



class ChannelStack(argschema.schemas.DefaultSchema):
    channel = argschema.fields.Str(required=False,
                                   description="Channel of stack to render (if needed)")
    stack = argschema.fields.Str(required=True, 
                                 description="render stack to render")
    maxIntensity = argschema.fields.Int(required=False, 
                                        description="Max intensity to render this channel")
    
class MakeAnnotationSynaptogramParameters(RenderParameters):
    global_annotation_file = argschema.fields.InputFile(required=True,
                                                        description = "global annotation file")
    fig_directory = argschema.fields.OutputDir(required=True,
                                            description = "directory to store figures")
    annotation_metadata_json = argschema.fields.OutputFile(required=True,
                                                          description = "where to save metadata")
    channel_stacks = argschema.fields.Nested(ChannelStack,
                                             many=True,
                                             required=True,
                                             description="list of Channel Stacks to render")
    synapses_to_make=argschema.fields.List(argschema.fields.Str,
                                           required=False,
                                          description="list of oid's to make synapses from")

    
    
def load_annotation_file(annotation_path):
    with open(annotation_path,'r') as fp:
            annotation_d = json.load(fp)
    schema = AnnotationFile()
    annotations,errors = schema.load(annotation_d)        
    assert(len(errors)==0)
    return annotations

def make_synaptogram(render,channel_stacks,savedir,al,border=400/3,borderz=2):
    oid = al['oid']
    zvalues = []
    Nareas = len(al['areas'])
    mins = np.zeros((Nareas,2))
    maxs = np.zeros((Nareas,2))
    for i,area in enumerate(al['areas']):
        zvalues.append(area['z'])
        gp = area['global_path']
        mins[i,:] = np.min(gp,axis=0)
        maxs[i,:] = np.max(gp,axis=0)
    gmins = np.min(mins,axis=0)-border
    gmaxs = np.max(maxs,axis=0)+border
    minX = gmins[0]
    minY = gmins[1]
    maxX = gmaxs[0]
    maxY = gmaxs[1]
    width = maxX-minX+1
    height = maxY-minY+1
    zvalues=sorted(zvalues)
    zvals = np.arange(np.min(zvalues)-1,np.max(zvalues)+1+1)
    Nz = len(zvals)
    Nc = len(channel_stacks)
    minZ = int(min(zvals))
    ratio = ((Nc)*(height)*1.05)/((Nz)*(width)*1.0)
    fig_width=.5*(width*Nz)/100.0
    print width,height,Nz
    d={
        'oid':oid,
        'id':al['id'],
        'minX':minX,
        'maxX':maxX,
        'minY':minY,
        'maxY':maxY,
        'Nz':Nz,
        'minZ':minZ,
        'maxZ':minZ+Nz,
        'width':width,
        'height':height
    }
    if width>1000:
        return d
    if height>1000:
        return d
    if len(zvals)>16:
        return d
    plt.rcParams['axes.facecolor'] = 'black'
    f,ax=plt.subplots(Nc,Nz,
                      figsize=(fig_width,int(fig_width*ratio)),
                      gridspec_kw = {'wspace':0, 'hspace':0},
                     facecolor='black')
    plt.subplots_adjust(left=0.0, right=1.0, top=1.0, bottom=0.0)
    for c,chstack in enumerate(channel_stacks):
        for zi,z in enumerate(zvals):
            a=ax[c,zi]
            a.set_xlim([minX,maxX])
            a.set_ylim([minY,maxY])
            a.set_xticks([])
            a.set_yticks([])
            a.set_aspect('equal')
            chname = chstack.get('channel',None)
            maxIntensity = chstack.get('maxIntensity',None)
            img = renderapi.image.get_bb_image(chstack['stack'],
                                               z,
                                               minX,
                                               minY,
                                               width,
                                               height,
                                               channel=chname,
                                               maxIntensity=maxIntensity,
                                               render=render)
            a.imshow(img,vmin=0,vmax=255,extent=[minX,maxX,maxY,minY])
    for i,area in enumerate(al['areas']):
        zi = int(area['z']-minZ)
        for c in range(1,len(channel_stacks)):
            a = ax[c,zi]
            a.plot(area['global_path'][:,0],area['global_path'][:,1],c='Teal',linewidth=2)
    for c,chstack in enumerate(channel_stacks):
        chname = chstack.get('channel',chstack['stack'])
        
        ax[c,0].text(minX,minY,chname[0:4],fontdict={'color':'SLATEGRAY','weight':'bold'},fontsize=14)
    #f.tight_layout(True)
    fname = os.path.join(savedir,'{}.png'.format(oid))
    f.savefig(fname)
    d['figure']=fname
    plt.clf()
    plt.close()
    del(f)
    return d


class MakeAnnotationSynaptograms(RenderModule):
    default_schema = MakeAnnotationSynaptogramParameters
    
    def run(self):
        print self.args
        annotations = load_annotation_file(self.args['global_annotation_file'])
    
        if not os.path.isdir(self.args['fig_directory']):
            os.makedirs(self.args['fig_directory'])
        
        
        myp = partial(make_synaptogram,
                      self.render,
                      self.args['channel_stacks'],
                      self.args['fig_directory'])
      
        #print disagree_oids
        proc_pool= pool.Pool(6)
        good_oids = self.args.get('synapses_to_make',None)
        if good_oids is not None:
            good_ann =[al for al in annotations['area_lists'] if al['oid'] in good_oids]
            ds = proc_pool.map(myp,good_ann)
        else:
            ds=proc_pool.map(myp,annotations['area_lists'])
        print(len(ds)) 
        with open(self.args['annotation_metadata_json'],'w') as fp:
            json.dump(ds,fp)
                         
            
if __name__ == '__main__':            
    mod = MakeAnnotationSynaptograms(input_data = example_parameters)
    mod.run()
