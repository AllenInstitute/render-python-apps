#!/usr/bin/env python
import os
import sys
import renderapi 
from renderapi.tilespec import TileSpec
from renderapi.transform import AffineModel
from renderapi.utils import stripLogger
import logging
import argparse
from trakem2utils import createchunks,createheader,createproject,createlayerset,createfooters,createlayer_fromtilespecs,Chunk
import  json
from renderapps.module.render_module import TEM2ProjectTransfer, TrakEM2RenderModule, EMLMRegistrationParameters
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
    mod = TrakEM2RenderModule(schema_type=TEM2ProjectTransfer,input_data=example_parameters)

    zvalues = mod.render.run(renderapi.stack.get_z_values_for_stack,mod.args['inputStack'])

    minZ = mod.args.get('minZ',int(np.min(zvalues)))
    maxZ = mod.args.get('maxZ',int(np.max(zvalues)))

    if mod.args['doChunk']:
        allchunks = createchunks(minZ,maxZ,mod.args['chunkSize'])
        raise Exception('do chunk output not yet implemented')
    else:
        allchunks=[]
        ck = Chunk()
        ck.first = minZ
        ck.last = maxZ
        ck.dir = str(ck.first)+ "-" + str(ck.last)
        allchunks.append(ck)

    for x in allchunks:

        indir = os.path.join(mod.args['outputXMLdir'],x.dir)
        infile=os.path.join(indir,'project.xml')
        outfile = os.path.join(indir,'tilespec.json')

        mod.convert_trakem2_project(infile,indir,outfile)

        with open(outfile,'r') as fp:
            tsjson = json.load(fp)

        output_tilespecs = [TileSpec(json=tsj) for tsj in tsjson]
        shiftTransform = AffineModel(B0=mod.args['minX'],B1=mod.args['minY'])
        jsonfiles=[]
        for layerid in range(x.first, x.last+1):    
            print 'layerid',x.first
            jsonfilename = os.path.join(mod.args['outputXMLdir'],'%05d.json'%layerid)
            output_tilespec_list = []
            tilespecs_original = renderapi.tilespec.get_tile_specs_from_minmax_box(
                mod.args['inputStack'],
                layerid,
                mod.args['minX'],
                mod.args['maxX'],
                mod.args['minY'],
                mod.args['maxY'],
                render=mod.render)
            for tso in tilespecs_original:
                matches = [ts for ts in output_tilespecs if ts.tileId==tso.tileId]
                if len(matches)>0:
                    tsm = matches[0]
                    tso.tforms = tsm.tforms
                    tso.tforms.append(shiftTransform)
                    output_tilespec_list.append(tso)
            with open(jsonfilename,'w') as fp:
                renderapi.utils.renderdump(output_tilespec_list,fp,indent=4)
            jsonfiles.append(jsonfilename)

        if not mod.args['doChunk']:
            #renderapi.stack.delete_stack(mod.args['outputStack'],render=r) 
            renderapi.stack.create_stack(mod.args['outputStack'],render=mod.render)
            renderapi.client.import_jsonfiles_parallel(mod.args['outputStack'],jsonfiles,render=mod.render)
