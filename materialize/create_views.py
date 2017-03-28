#!/usr/bin/env python

import argparse
import os
import json
import renderapi
import random
import requests
import tifffile
from PIL import Image
from io import BytesIO
import numpy as np
import pathos.multiprocessing as mp
from functools import partial

if __name__ == '__main__':
    DEFAULT_HOST='ibs-forrestc-ux1.corp.alleninstitute.org'
    DEFAULT_PORT = 8080
    parser = argparse.ArgumentParser(description = "Create Views for Movie")
    parser.add_argument('--inputStacks',nargs='*',help='Name of input stack',type=str)
    parser.add_argument('--outputDirectory',help='Output directory',type=str,required=True)
    parser.add_argument('--scale',help='Scale of image',type=float,default=1.0)
    parser.add_argument('--firstz',help='First z value (defaults to first z) ',type=int)
    parser.add_argument('--lastz',help='Last z value (defaults to last z)',type=int)
    parser.add_argument('--x',help='left x value',type=int,required=True)
    parser.add_argument('--y',help='top y value',type=int,required=True)
    parser.add_argument('--width',help='image width',type=int,required=True)
    parser.add_argument('--height',help='image height',type=int,required=True)
    parser.add_argument('--skip',help='Number of Sections to skip over ',type=int,default=10)
    parser.add_argument('--owner',help='Render Owner',type=str,required=True)
    parser.add_argument('--project',help='Render project',type=str,required=True)
    parser.add_argument('--host',help='render host',type=str,default=DEFAULT_HOST)
    parser.add_argument('--port',help='render port',type=int,default=DEFAULT_PORT)

    args = parser.parse_args()

    print args.lastz

    render = renderapi.Render(args.host,args.port,args.owner,args.project)
    zvalues = render.get_z_values_for_stack(args.inputStacks[0],verbose=True)
    #print args.inputStacks,zvalues,args.owner,args.project
    minz = np.min(zvalues)
    maxz = np.max(zvalues)
    print minz,maxz
    if args.firstz is None:
        args.firstz = minz
    else:
        assert(args.firstz>=minz),'firstz %d too small, minz %d'%(args.firstz,minz)
    if args.lastz is None:
        args.lastz = maxz
    else:
        assert(args.lastz<=maxz),'lastz %d too big, maxz %d'%(args.lastz,maxz)

    
    for stack in args.inputStacks:
        endpath = os.path.join(args.outputDirectory,stack)
        if not os.path.isdir(endpath):
            os.makedirs(endpath)
    zvalues = np.arange(args.firstz,args.lastz,args.skip)
    def process_z(stack,z):
        endpath = os.path.join(args.outputDirectory,stack)
        data = render.get_png_tile(stack,z,args.x,args.y,args.width,args.height,args.scale)
        data=data[:,:,0]
        outfilename = os.path.join(endpath,'%s_z_%04d.png'%(stack,z))
        im = Image.fromarray(data)
        im.save(outfilename)
    pool =mp.ProcessingPool(5)

    for stack in args.inputStacks:
    
        prt = partial(process_z,stack)
        res=pool.amap(prt,zvalues)
        res.wait()

