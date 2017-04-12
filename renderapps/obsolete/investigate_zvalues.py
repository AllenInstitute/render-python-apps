# import argparse
# import jsonschema
# import json
# import os
# import subprocess
# import copy
# from tilespec import TileSpec,Layout,AffineModel
# import numpy as np
# import json
# import glob
# from renderapi import Render

# if __name__ == '__main__':
#     raise(Exception('THIS NEEDS TO BE UPDATED FOR NEW API'))
#     parser = argparse.ArgumentParser(description="Create Stitched Stack to be used for alignment")
#     parser.add_argument('--inputStack', nargs=1, help='output stack', type=str)
#     args = parser.parse_args()

#     stack = args.inputStack[0]    
#     render = Render("ibs-forrestc-ux1.corp.alleninstitute.org", 8082, "Sharmishtaas", "M270907_Scnn1aTg2Tdt_13")
#     allz = render.get_z_values_for_stack(stack)
#     print len(allz)

    
