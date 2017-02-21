#!/usr/bin/env python
import os
import sys
sys.path.insert(0,'/data/array_tomography/ImageProcessing/render-python/')
#sys.path.insert(0,'/nas3/data/M270907_Scnn1aTg2Tdt_13/scripts_ff/')
import renderapi

import argparse
from trakem2utils import createchunks,createheader,createproject,createlayerset,createfooters,createlayer_fromtilespecs,Chunk
import  json
def merge_two_dicts(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = "Create xml from stack")
    parser.add_argument('--inputJson',help='json based input argument file',type=str)
    parser.add_argument('--inputStack',help="input stack",type=str,required=False)
    parser.add_argument('--minX',help="input stack",type=str,required=False)
    parser.add_argument('--minY',help="input stack",type=str,required=False)
    parser.add_argument('--maxX',help="input stack",type=str,required=False)
    parser.add_argument('--maxY',help="input stack",type=str,required=False)
    parser.add_argument('--host',help="input stack",type=str,required=False,default= 'ibs-forrestc-ux1')
    parser.add_argument('--port',help="input stack",type=str,required=False,default = 8080)
    parser.add_argument('--owner',help="input stack",type=str,required=False)
    parser.add_argument('--project',help="input stack",type=str,required=False)
    parser.add_argument('--minZ',help="input stack",type=str,required=False)
    parser.add_argument('--maxZ',help="input stack",type=str,required=False)
    parser.add_argument('--doChunk',help="input stack",type=str,required=False)
    parser.add_argument('--chunkSize',help="input stack",type=str,required=False)
    parser.add_argument('--outputXMLdir',help="input stack",type=str,required=False)
    parser.add_argument('--badSections',nargs='*',help='section zs to leave out',type=int,required=False,default = [])
    parser.add_argument('--client_scripts',help='client scripts directory',type=str,required=False,
        default ="/pipeline/render/render-ws-java-client/src/main/scripts")
    args = parser.parse_args()
    if args.inputJson is not None:
        jsonstring = open(args.inputJson,'r').read()
        jsonargs = json.loads(jsonstring)
        mainargs = vars(args)
        #print mainargs
        args = merge_two_dicts(mainargs,jsonargs)
    else:
        args = vars(args)

    if args['doChunk']:
        allchunks = createchunks(args['firstSection'],args['lastSection'],args['sectionsPerChunk'])
    else:
        allchunks=[]
        ck = Chunk()
        ck.first = args['minZ']
        ck.last = args['maxZ']
        ck.dir = str(ck.first)+ "-" + str(ck.last)
        allchunks.append(ck)

    layersetfile = "layerset.xml"
    headerfile = "header.xml"
    r = renderapi.render.connect(host=args['host'], port=args['port'], owner=args['owner'],
project=args['project'], client_scripts=args['client_scripts'])
    #render = Render(args['host'],args['port'],args['owner'],args['project'],args)
    #stackmetadata=render.get_stack_metadata_by_owner(args['owner'])
    #stackmetadata=[smd for smd in stackmetadata if ((smd['stackId']['project']==args['project']) and (smd['stackId']['stack']==args['inputStack']))]
    #stackbounds = stackmetadata[0]['stats']['stackBounds']
    #print stackbounds
    for x in allchunks:
        #inputargs
        print args['outputXMLdir'],args['minZ']
        print jsonargs['outputXMLdir']
        outdir = os.path.join(args['outputXMLdir'],x.dir)
        outfile=os.path.join(outdir,'project.xml')
        if not os.path.exists(outdir):
                os.makedirs(outdir)

        #copy header
        createheader(headerfile,outfile)
        #create project
        createproject(outfile)
        #create layerset
        createlayerset(outfile,width=(args['maxX']-args['minX']),height=(args['maxY']-args['minY']))
        #add layers
        
        for layerid in range(x.first, x.last):
            print "This is layerid:"        
            print layerid
            if layerid not in args['badSections']:
                tilespecs = render.tilespec.get_tile_specs_from_minmax_box(
                    args['inputStack'],
                    layerid,
                    args['minX'],
                    args['maxX'],
                    args['minY'],
                    args['maxY'],
                    render=r)
                print "Now adding layer: %d \n %d tiles"%(layerid,len(r))
                createlayer_fromtilespecs(tilespecs, outfile,layerid,shiftx=-args['minX'],shifty=-args['minY'])
            else:
               	tilespecs = None
                
        #footers
        print outfile
        createfooters(outfile)
