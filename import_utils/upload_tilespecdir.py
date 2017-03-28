import argparse
import jsonschema
import json
import os
import pandas as pd
import subprocess
import copy
from tilespec import TileSpec,Layout,AffineModel
import numpy as np
from sh import tar,zip
import json
import glob
import sys
sys.path.insert(0,'/data/array_tomography/ImageProcessing/render-python/')
from renderapi import Render

if __name__ == '__main__':

    DEFAULT_HOST = "ibs-forrestc-ux1.corp.alleninstitute.org"
    DEFAULT_PORT = 8080
    DEFAULT_OWNER = "Forrest"
    DEFAULT_PROJECT = "TEST"

    parser = argparse.ArgumentParser(description="Upload a full directory of tilespecs without extra transform references.")
    parser.add_argument('--inputDir', nargs=1, help='tilespec directory', type=str)
    parser.add_argument('--outputStack', nargs=1, help='output stack', type=str)
    parser.add_argument('--owner',default=DEFAULT_OWNER,required=False)
    parser.add_argument('--project',default=DEFAULT_PROJECT,required=False)
    parser.add_argument('--host',default=DEFAULT_HOST,required=False)
    parser.add_argument('--port',default=8080,required=False)

    args = parser.parse_args()

    jsonfiles = sorted(glob.glob(args.inputDir[0]+"*.json"))
    print jsonfiles
    
    render = Render(args.host,args.port,args.owner,args.project)
    render.create_stack(args.outputStack[0])
    render.import_jsonfiles_parallel(args.outputStack[0],jsonfiles)
