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
from renderapi import Render

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Create Stitched Stack to be used for alignment")
    parser.add_argument('--inputDir', nargs=1, help='tilespec directory', type=str)
    parser.add_argument('--outputStack', nargs=1, help='output stack', type=str)
    parser.add_argument('--channel',nargs=1,help='channel',type=str)
    args = parser.parse_args()

    str = args.inputDir[0]+"/"+args.channel[0] + "*.json"
    print str

    jsonfiles = sorted(glob.glob(str))
    print jsonfiles
    
    render = Render("ibs-forrestc-ux1.corp.alleninstitute.org", 8080, "Sharmishtaas", "M270907_Scnn1aTg2Tdt_13")

    render.create_stack(args.outputStack[0])
    render.import_jsonfiles_one_by_one(args.outputStack[0],jsonfiles)

