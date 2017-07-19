#!/usr/bin/env python
import math
import json
import random
from renderapi.transform import AffineModel

def randomDig(digits):
    lower = 10**(digits-1)
    upper = 10**digits - 1
    return random.randint(lower,upper)

def createproject(outfile):
    lines = []
    outdirectory,myfile = outfile.rsplit("/",1)
    p1 = randomDig(13)
    p2 = randomDig(9)
    p3 = randomDig(10)
    strdir = str(p1)+"."+str(p2)+"."+str(p3)

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


def createlayer_fromtilespecs(tilespecs, outfile, layerid,shiftx=0.0,shifty=0.0,affineOnly=False):
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
        createpatch(tilespecs, lines, patchid,layerid,shiftx=shiftx,shifty=shifty,affineOnly=affineOnly)
        patchid = patchid + 1

    # end layer
    lines.append("\t</t2_layer>\n")
    layerid = layerid + 1

    with open(outfile, "a") as f1:
        f1.writelines(lines)


def createpatch(tilespecs, lines, patchid,layerid,shiftx=0.0,shifty=0.0,affineOnly=False):
    import numpy as np
    ts = tilespecs[patchid]
    #fp = tilespecs[patchid]['mipmapLevels']['0']['imageUrl']
    #print fp
    #fp = fp.replace("raw/data","processed/flatfieldcorrecteddata")
    #fp = fp.replace("session","Session000")
    fp = ts.ip.get(0)['imageUrl']
    #left,right = fp.split('_F',1)
    #num,rright = right.split('_',1)
    #lenspeclist = len(tilespecs[patchid]['transforms']['specList'])
    lenspeclist = len(ts.tforms)
    #tString = tilespecs[patchid]['transforms']['specList'][lenspeclist-1]['dataString']
    #print tilespecs[patchid].tforms[lenspeclist-1]

    if affineOnly:
        tform_total = AffineModel()
        for tform in ts.tforms:
            tform_total = tform.concatenate(tform_total)
        M00 = str(tform_total.M00)
        M10 = str(tform_total.M01)
        M01 = str(tform_total.M10)
        M11 = str(tform_total.M11)
        B0 = str(tform_total.B0+shiftx)
        B1 = str(tform_total.B1+shifty)
    else:
        B0 = str(ts.minX+shiftx)
        B1 = str(ts.minY+shifty)
        M00 = str(1.0)
        M01 = str(0.0)
        M10 = str(0.0)
        M11 = str(1.0)
	    #B0 = str(0)
    #B1 = str(0)
    #    local_corners = np.array([[0,0],[0,ts.height],[ts.width,ts.height],[ts.width,0],[0,0]])
    #    world_corners = render.local_to_world_coordinates_array()
    #world_corners = tform_total.tform(local_corners)
    #mins= np.min(world_corners,axis=0)



    fname = fp.split('/')
    filename_only = fp
    filename_only=filename_only.replace('file:','').replace('%20',' ')

    lines.append("\t<t2_patch\n")
    #lines.append("\toid='" + str(patchid+(1000*layerid)) + "'\n")
    lines.append("\toid= '" + ts.tileId +  "'\n")
    lines.append("\twidth='" + str(ts.width)+"'\n")
    lines.append("\theight='" + str(ts.height) + "'\n")
    #lines.append("\ttransform='matrix(" + t[0] + "," + t[1] + "," + t[2] + "," + t[3] + "," + t[4] + "," + t[5] + ")'\n")
    lines.append("\ttransform='matrix(" + M00 + "," + M01 + "," + M10 + "," + M11 + "," + B0 + "," + B1 + ")'\n")
    lines.append("\tlinks=''\n")
    lines.append("\ttype='1'\n")
    lines.append("\tfile_path='" + filename_only + "'\n")
    lines.append("\ttitle= '" + ts.tileId +  "'\n")
    lines.append("\tstyle='fill-opacity:1.0;stroke:#ffff00;'\n")
    lines.append("\to_width='" + str(int(ts.width))+"'\n")
    lines.append("\to_height='" + str(int(ts.height)) + "'\n")
    lines.append("\tmin= '" + str(ts.minint) +  "'\n")
    lines.append("\tmax= '" + str(ts.maxint) +  "'\n")
    lines.append("\tmres='32'\n")
    lines.append("\t>\n")
    if not affineOnly:
        lines.append("\t<ict_transform_list>\n")
        for tform in ts.tforms:
            tformdict = tform.to_dict()
            lines.append("\t\t<iict_transform class='%s' data='%s' />\n"%(tformdict['className'],tformdict['dataString']))
        lines.append("\t</ict_transform_list>\n")
    lines.append("\t</t2_patch>\n")

def createheader(headerfile,outfile):
    with open(headerfile) as f:
        lines = f.readlines()
        with open(outfile, "w") as f1:
            f1.writelines(lines)

def createlayerset(outfile,width=7000,height=7000):
    lines = []
    lines.append('<t2_layer_set\n')
    lines.append('oid="3"\n')
    lines.append('width="%f"\n'%width)
    lines.append('height="%f"\n'%height)
    lines.append('transform="matrix(1.0,0.0,0.0,1.0,0.0,0.0)"\n')
    lines.append('title="Top Level"\n')
    lines.append('links=""\n')
    lines.append('layer_width="%f"\n'%width)
    lines.append('layer_height="%f"\n'%height)
    lines.append('rot_x="0.0"\n')
    lines.append('rot_y="0.0"\n')
    lines.append('rot_z="0.0"\n')
    lines.append('snapshots_quality="true"\n')
    lines.append('snapshots_mode="Full"\n')
    lines.append('color_cues="true"\n')
    lines.append('area_color_cues="true"\n')
    lines.append('avoid_color_cue_colors="false"\n')
    lines.append('n_layers_color_cue="0"\n')
    lines.append('paint_arrows="true"\n')
    lines.append('paint_tags="true"\n')
    lines.append('paint_edge_confidence_boxes="true"\n')
    lines.append('prepaint="false"\n')
    lines.append('preload_ahead="0"\n')
    lines.append('>\n')
    with open(outfile, "a") as f1:
        f1.writelines(lines)

def createfooters(outfile):
    lines = []
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
