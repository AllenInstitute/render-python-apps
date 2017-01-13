#!/usr/bin/env python

import os
import json
#import renderapi_sharmi
import sys
sys.path.insert(0,'/data/array_tomography/ImageProcessing/render-python/')
#sys.path.insert(0,'/nas3/data/M270907_Scnn1aTg2Tdt_13/scripts_ff/')
from renderapi import Render
import random
import argparse
import math

def randomDig(digits):
    lower = 10**(digits-1)
    upper = 10**digits - 1
    return random.randint(lower,upper)

def createproject(outfile):
    lines = [];
    outdirectory,myfile = outfile.rsplit("/",1)
    p1 = randomDig(13)
    p2 = randomDig(9)
    p3 = randomDig(10)
    strdir = str(p1)+"."+str(p2)+"."+str(p3);

    lines.append("\tunuid='" + strdir + "'\n")
    lines.append("\tmipmaps_folder='" + outdirectory + "/trakem2." + strdir + "/trakem2.mipmaps/'\n")
    lines.append("\tstorage_folder='" + outdirectory + "/'\n")
    lines.append("\tmipmaps_format='4'\n")
    lines.append("\timage_resizing_mode='Area downsampling'\n")
    lines.append("\t>\n")
    lines.append("\t</project>\n")
    lines.append("\n")

    with open(outfile, "a") as f1:
        f1.writelines(lines)


def createlayer(jsonfile, outfile, layerid):
    tilespecs = json.load(open(jsonfile, 'r'))
    lines = []
    #lines.append("\t<t2_layer oid='" + str(layerid) + "'\n")
    lines.append("\tthickness='1.0'\n")
    lines.append("\tz='0.0'\n")
    lines.append("\ttitle='" + str(layerid) + "'\n")
    lines.append("\t>\n")

    patchid = 0
    #Ntiles = len(tilespecs['tileSpecs'])
    Ntiles = len(tilespecs)
    
    print "This is the number of tiles:"
    print Ntiles
    
    y = 0
    while patchid < Ntiles:
    #print patchid
        createpatch(tilespecs, lines, patchid,layerid)
        patchid = patchid + 1

    # end layer
    lines.append("\t</t2_layer>\n")
    layerid = layerid + 1

    with open(outfile, "a") as f1:
        f1.writelines(lines)


def createlayer_fromtilespecs(tilespecs, outfile, layerid):
    #tilespecs = json.load(open(jsonfile, 'r'))
    lines = []
    lines.append("\t<t2_layer oid='" + str(layerid+10) + "'\n")
    lines.append("\tthickness='1.0'\n")
    lines.append("\tz='"+str(layerid)+"'\n")
    #lines.append("\ttitle=''\n")
    lines.append("\ttitle='layer_" + str(layerid) + "'\n")
    lines.append("\t>\n")

    patchid = 0
    #Ntiles = len(tilespecs['tileSpecs'])
    Ntiles = len(tilespecs)
    
    #print "This is the number of tiles:"
    #print Ntiles
    
    y = 0
    while patchid < Ntiles:
    #print patchid
        createpatch(tilespecs, lines, patchid,layerid)
        patchid = patchid + 1

    # end layer
    lines.append("\t</t2_layer>\n")
    layerid = layerid + 1

    with open(outfile, "a") as f1:
        f1.writelines(lines)


def createpatch(tilespecs, lines, patchid,layerid):

    #fp = tilespecs[patchid]['mipmapLevels']['0']['imageUrl']
    #print fp
    #fp = fp.replace("raw/data","processed/flatfieldcorrecteddata")
    #fp = fp.replace("session","Session000")
    fp = tilespecs[patchid].imageUrl
    left,right = fp.split('_F',1)
    num,rright = right.split('_',1)
    #lenspeclist = len(tilespecs[patchid]['transforms']['specList'])
    lenspeclist = len(tilespecs[patchid].tforms)
    #tString = tilespecs[patchid]['transforms']['specList'][lenspeclist-1]['dataString']
    print tilespecs[patchid].tforms[lenspeclist-1]
    M00 = str(tilespecs[patchid].tforms[lenspeclist-1].M00)
    M01 = str(tilespecs[patchid].tforms[lenspeclist-1].M01)
    M10 = str(tilespecs[patchid].tforms[lenspeclist-1].M10)
    M11 = str(tilespecs[patchid].tforms[lenspeclist-1].M11)
    B0 = str(tilespecs[patchid].tforms[lenspeclist-1].B0)
    B1 = str(tilespecs[patchid].tforms[lenspeclist-1].B1)
    

    fname = fp.split('/')
    filename_only = fp
    
    lines.append("\t<t2_patch\n")
    #lines.append("\toid='" + str(patchid+(1000*layerid)) + "'\n")
    lines.append("\toid= '" + tilespecs[patchid].tileId +  "'\n")
    lines.append("\twidth='" + str(tilespecs[patchid].width)+"'\n")
    lines.append("\theight='" + str(tilespecs[patchid].height) + "'\n")
    #lines.append("\ttransform='matrix(" + t[0] + "," + t[1] + "," + t[2] + "," + t[3] + "," + t[4] + "," + t[5] + ")'\n")
    lines.append("\ttransform='matrix(" + M00 + "," + M01 + "," + M10 + "," + M11 + "," + B0 + "," + B1 + ")'\n")
    lines.append("\tlinks=''\n")
    lines.append("\ttype='1'\n")    
    lines.append("\tfile_path='" + filename_only + "'\n")
    lines.append("\ttitle= '" + tilespecs[patchid].tileId +  "'\n")
    lines.append("\tstyle='fill-opacity:1.0;stroke:#ffff00;'\n")
    lines.append("\to_width='" + str(int(tilespecs[patchid].width))+"'\n")
    lines.append("\to_height='" + str(int(tilespecs[patchid].height)) + "'\n")
    lines.append("\tmin= '" + str(tilespecs[patchid].minint) +  "'\n")
    lines.append("\tmax= '" + str(tilespecs[patchid].maxint) +  "'\n")
    lines.append("\tmres='32'\n")
    lines.append("\t>\n")
    lines.append("\t</t2_patch>\n")

def createheader(headerfile,outfile):
    with open(headerfile) as f:
        lines = f.readlines()
        with open(outfile, "w") as f1:
            f1.writelines(lines)

def createlayerset(layersetfile,outfile):
    with open(layersetfile) as f:
        lines = f.readlines()
        with open(outfile, "a") as f1:
            f1.writelines(lines)

def createfooters(outfile):
    lines = [];
    lines.append("\t</t2_layer_set>\n")
    lines.append("\t</trakem2>\n")
    
    with open(outfile, "a") as f1:
	print lines
        f1.writelines(lines)

class Chunk:
    first = 0
    last = 10
    dir = ""

def createchunks(firstSection,lastSection,sectionsPerChunk):
    if sectionsPerChunk % 2 > 0:
        print "Please Input an even number of sections per chunk!"
        exit(0)

    allchunks = []
    numchunks = int(math.ceil((lastSection-firstSection+1)/sectionsPerChunk))
    halfsz = int(sectionsPerChunk/2)

    #for x in range(firstSection,lastSection):
    x = firstSection
    while x < lastSection:
        ck = Chunk()
        ck.first = x
        if (x + sectionsPerChunk > lastSection):
            ck.last = lastSection + 1
        else:   
            ck.last = x + sectionsPerChunk 
        ck.dir = str(ck.first)+ "-" + str(ck.last)
        allchunks.append(ck)
        x = x + halfsz  
        
    return allchunks
        



if __name__ == '__main__':

    DEFAULT_HOST = "ibs-forrestc-ux1.corp.alleninstitute.org"
    DEFAULT_PORT = 8080
    DEFAULT_OWNER = "Sharmishtaas"
    DEFAULT_PROJECT = "M270907_Scnn1aTg2Tdt_13"
    DEFAULT_CLIENT_SCRIPTS = "/pipeline/render/render-ws-java-client/src/main/scripts"

    parser = argparse.ArgumentParser(description = "Create xml from stack")
    parser.add_argument('--inputStack',nargs=1,help='Input stack in render',type=str)
    parser.add_argument('--outputDirectory',nargs=1,help='Output directory location for xml projects',type=str)
    parser.add_argument('--sectionsPerChunk',nargs=1,help='Output directory location for xml projects',type=int)
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
        createlayerset(layersetfile, outfile)
        #add layers
        render = Render(args.host,args.port,args.owner,args.project)
        for layerid in range(x.first, x.last):
            print "This is layerid:"        
            print layerid
	    if layerid not in badsections:
            	r = render.get_tile_specs_from_z(args.inputStack[0],layerid)
	    else:
		r = None
	    print r
                #r = renderapi_sharmi.get_tile_specs_from_z(args.inputStack[0],layerid)
            if (r is None):
                print "r is none!"
            else:
                print badsections
                if layerid not in badsections:
                    print "Now adding layer: %d "%layerid
                    createlayer_fromtilespecs(r, outfile,layerid)
                layerid = layerid + 1
                
    	#footers
    	print outfile
    	createfooters(outfile)
