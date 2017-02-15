#!/usr/bin/env python
import os
import sys
sys.path.insert(0,'/data/array_tomography/ImageProcessing/render-python/')
#sys.path.insert(0,'/nas3/data/M270907_Scnn1aTg2Tdt_13/scripts_ff/')
from renderapi import Render
from tilespec import TileSpec, AffineModel
import argparse
from trakem2utils import createchunks,createheader,createproject,createlayerset,createfooters,createlayer_fromtilespecs,Chunk
import  json


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = "Create xml from stack")
    parser.add_argument('--inputJson',help='json based input argument file',type=str)
    parser.add_argument('--outputJson',help='json to describe where to output',type=str)
     
    args = parser.parse_args()

    jsonstring = open(args.inputJson,'r').read()
    jsonargs = json.loads(jsonstring)

    outputjsonstring = open(args.outputJson,'r').read()
    jsonoutputargs = json.loads(outputjsonstring)

    if jsonargs['doChunk']:
        allchunks = createchunks(jsonargs['minZ'],jsonargs['maxZ'],jsonargs['sectionsPerChunk'])
    else:
        allchunks=[]
        ck = Chunk()
        ck.first = jsonargs['minZ']
        ck.last = jsonargs['maxZ']
        ck.dir = str(ck.first)+ "-" + str(ck.last)
        allchunks.append(ck)
    render = Render(jsonargs['host'],jsonargs['port'],jsonargs['owner'],jsonargs['project'])

    for x in allchunks:

        indir = os.path.join(jsonargs['outputXMLdir'],x.dir)
        infile=os.path.join(indir,'project.xml')
        outfile = os.path.join(indir,'tilespec.json')

        renderAppDir= os.path.join(jsonoutputargs['renderHome'],'render-app','target')
        renderJar = [os.path.join(renderAppDir,f) for f in os.listdir(renderAppDir)\
         if (f.startswith('render-app') and f.endswith('jar-with-dependencies.jar'))][0]
        print renderJar
        
        cmd = ['java','-cp',renderJar,'org.janelia.alignment.trakem2.Converter',infile,indir,outfile]
        #os.system(' '.join(cmd))

        with open(outfile,'r') as fp:
            tsjson = json.load(fp)
        output_tilespecs = [TileSpec(json=tsj) for tsj in tsjson]
        shiftTransform = AffineModel(B0=jsonargs['minX'],B1=jsonargs['minY'])
        jsonfiles=[]
        for layerid in range(x.first, x.last):    
            jsonfilename = os.path.join(jsonargs['outputXMLdir'],'%05d.json'%layerid)

            tilespecs_original = render.get_tile_specs_from_minmax_box(
                jsonargs['inputStack'],
                layerid,
                jsonargs['minX'],
                jsonargs['maxX'],
                jsonargs['minY'],
                jsonargs['maxY'])
            for tso in tilespecs_original:
                tsm = next(ts for ts in output_tilespecs if ts.tileId==tso.tileId)
                tso.tforms = tsm.tforms
                tso.tforms.append(shiftTransform)
            with open(jsonfilename,'w') as fp:
                json.dump([ts.to_dict() for ts in tilespecs_original],fp,indent=4)
            jsonfiles.append(jsonfilename)
        if not jsonargs['doChunk']:
            render.create_stack(jsonoutputargs['outputStack'])         
            render.import_jsonfiles_parallel(jsonoutputargs['outputStack'],jsonfiles)
            
#             print "This is layerid:"        
#             print layerid
#             if layerid not in args['badSections']:
#                 r = render.get_tile_specs_from_minmax_box(args['inputStack'],layerid,args['minX'],args['maxX'],args['minY'],args['maxY'])
# #                r = render.get_tile_specs_from_z(args['inputStack'],layerid)
#                 print "Now adding layer: %d \n %d tiles"%(layerid,len(r))
#                 createlayer_fromtilespecs(r, outfile,layerid)
#             else:
#                	r = None
                
#         #footers
#         print outfile
#         createfooters(outfile)
