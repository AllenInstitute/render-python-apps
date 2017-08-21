#!/usr/bin/env python
import os
import sys
sys.path.insert(0,'/data/array_tomography/ImageProcessing/render-python/')
#sys.path.insert(0,'/nas3/data/M270907_Scnn1aTg2Tdt_13/scripts_ff/')
import renderapi
import argparse
from trakem2utils import createchunks,createheader,createproject,createlayerset,createfooters,createlayer_fromtilespecs

if __name__ == '__main__':

    DEFAULT_HOST = "ibs-forrestc-ux1.corp.alleninstitute.org"
    DEFAULT_PORT = 8080
    DEFAULT_OWNER = "Sharmishtaas"
    DEFAULT_PROJECT = "M270907_Scnn1aTg2Tdt_13"
    DEFAULT_CLIENT_SCRIPTS = "/pipeline/render/render-ws-java-client/src/main/scripts"

    parser = argparse.ArgumentParser(description = "Create xml from stack")
    parser.add_argument('--inputStack',nargs=1,help='Input stack in render',type=str)
    parser.add_argument('--outputDirectory',nargs=1,help='Output directory location for xml projects',type=str)
    parser.add_argument('--sectionsPerChunk',nargs=1,help='Number of sections per chunk',type=int)
    parser.add_argument('--firstSection',nargs=1,help='First Section',type=int)
    parser.add_argument('--lastSection',nargs=1,help='Last Section',type=int)
    parser.add_argument('--owner',default=DEFAULT_OWNER,required=False)
    parser.add_argument('--project',default=DEFAULT_PROJECT,required=False)
    parser.add_argument('--host',default=DEFAULT_HOST,required=False)
    parser.add_argument('--port',default=8080,required=False)


    args = parser.parse_args()

    badsections=[80,135,723,780,1219,1220,1221,1244,1271,1272,1299,1300,1470,1767,1714,1715,1820,1821,1960,1966,1967,2078,2287,2288,2297,2305,2333,2334,2388,2391,2440,2547]
    #badsections=[]
    allchunks = createchunks(args.firstSection[0],args.lastSection[0],args.sectionsPerChunk[0])
    layersetfile = "layerset.xml"
    headerfile = "header.xml"


    for x in allchunks:
        #inputargs
        outfile=args.outputDirectory[0]+ "/" + x.dir + "/project.xml"
        print outfile
        if not os.path.exists(args.outputDirectory[0]+ "/" + x.dir):
                os.makedirs(args.outputDirectory[0]+ "/" + x.dir)
        #copy header
        createheader(headerfile,outfile)
        #create project
        createproject(outfile)
        #create layerset
        createlayerset(outfile)
        #add layers
        render = Render(args.host,args.port,args.owner,args.project)
        r = renderapi.connect(host=args.host, port=args.port, owner=args.owner,
project=args.project, client_scripts=args.client_scripts)
        for layerid in range(x.first, x.last):
            print "This is layerid:"        
            print layerid
            if layerid not in badsections:
                tilespecs = render.tilespecs.get_tile_specs_from_z(args.inputStack[0],layerid)
            else:
                tilespecs = None
            
            #r = renderapi_sharmi.get_tile_specs_from_z(args.inputStack[0],layerid)
            if (tilespecs is None):
                print "r is none!"
            else:
                print badsections
                if layerid not in badsections:
                    print "Now adding layer: %d "%layerid
                    createlayer_fromtilespecs(tilespecs, outfile,layerid)
                layerid = layerid + 1
                
        #footers
        print outfile
        createfooters(outfile)
