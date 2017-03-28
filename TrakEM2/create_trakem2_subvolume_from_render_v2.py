#!/usr/bin/env python
import os
import sys
#sys.path.insert(0,'/data/array_tomography/ImageProcessing/render-python/')
#sys.path.insert(0,'/nas3/data/M270907_Scnn1aTg2Tdt_13/scripts_ff/')
import renderapi
import logging
from renderapi.utils import stripLogger
import argparse
from trakem2utils import createchunks,createheader,createproject,createlayerset,createfooters,createlayer_fromtilespecs,Chunk
import json
from render_module import RenderModule,RenderParameters,TEM2ProjectTransfer
import json_module
import marshmallow as mm
import numpy as np

example_parameters = {
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":8080,
        "owner":"Forrest",
        "project":"M247514_Rorb_1",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    'minX':59945,
    'maxX':83341,
    'minY':84722,
    'maxY':138658,
    'minZ':24,
    'maxZ':24,
    'inputStack':'EM_fix',
    'outputStack':'EM_Site4_stitched',
    "doChunk":False,
    "outputXMLdir":"/nas3/data/M247514_Rorb_1/processed/Site4StitchFix/",
    "renderHome":"/pipeline/forrestrender/"
}


if __name__ == '__main__':

    mod = RenderModule(schema_type=TEM2ProjectTransfer,input_data=example_parameters)
    mod.run()

    zvalues = mod.render.run(renderapi.stack.get_z_values_for_stack,mod.args['inputStack'])

    minZ = mod.args.get('minZ',int(np.min(zvalues)))
    maxZ = mod.args.get('maxZ',int(np.max(zvalues)))

    if mod.args['doChunk']:
        allchunks = createchunks(minZ,maxZ,mod.args['chunkSize'])
    else:
        allchunks=[]
        ck = Chunk()
        ck.first = minZ
        ck.last = maxZ
        ck.dir = str(ck.first)+ "-" + str(ck.last)
        allchunks.append(ck)

    layersetfile = "layerset.xml"
    headerfile = "header.xml"

    for x in allchunks:

        outdir = os.path.join(mod.args['outputXMLdir'],x.dir)
        outfile=os.path.join(outdir,'project.xml')
        if not os.path.exists(outdir):
            os.makedirs(outdir)

        #copy header
        createheader(headerfile,outfile)
        #create project
        createproject(outfile)
        #create layerset
        createlayerset(outfile,width=(mod.args['maxX']-mod.args['minX']),height=(mod.args['maxY']-mod.args['minY']))
        #add layers
        
        for layerid in range(x.first, x.last+1):
            print "This is layerid:"        
            print layerid
            tilespecs = renderapi.tilespec.get_tile_specs_from_minmax_box(
                    mod.args['inputStack'],
                    layerid,
                    mod.args['minX'],
                    mod.args['maxX'],
                    mod.args['minY'],
                    mod.args['maxY'],
                    render=mod.render)
            print "Now adding layer: %d \n %d tiles"%(layerid,len(tilespecs))
            createlayer_fromtilespecs(tilespecs, outfile,layerid,shiftx=-mod.args['minX'],shifty=-mod.args['minY'])
                
        #footers
        print outfile
        createfooters(outfile)
