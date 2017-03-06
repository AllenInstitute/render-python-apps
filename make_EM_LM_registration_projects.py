import renderapi
from trakem2utils import createchunks,createheader,createproject,createlayerset,createfooters,createlayer_fromtilespecs,Chunk
import json
import logging
import os
import sys
from renderapi.utils import stripLogger
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = "Create xml files for each Z to register EM to LM")
    parser.add_argument('--inputJson',help='json based input argument file',type=str)
    parser.add_argument('--verbose','-v',help='verbose logging',action='store_true')
    args = parser.parse_args()

    jsonargs = json.load(open(args.inputJson,'r'))
   
    if not os.path.isdir(jsonargs['outputXMLdir']):
        os.makedirs(jsonargs['outputXMLdir'])
    EMstack = jsonargs['EMstack']
    LMstack = jsonargs['LMstack']
    r=renderapi.render.connect(**jsonargs['render'])
    EMz = renderapi.stack.get_z_values_for_stack(jsonargs['EMstack'],render=r)
    if args.verbose:
        stripLogger(logging.getLogger())
        logging.basicConfig(level=logging.DEBUG,stream=sys.stdout)
        logging.debug('verbose mode enabled!')

    layersetfile = "layerset.xml"
    headerfile = "header.xml"

    for z in EMz:
        outfile = os.path.join(jsonargs['outputXMLdir'],'%05d.xml'%z)
        createheader(headerfile,outfile)
        createproject(outfile)
        createlayerset(outfile,width=(jsonargs['maxX']-jsonargs['minX']),height=(jsonargs['maxY']-jsonargs['minY']))
        EMtilespecs = renderapi.tilespec.get_tile_specs_from_minmax_box(
                        EMstack,
                        z,
                        jsonargs['minX'],
                        jsonargs['maxX'],
                        jsonargs['minY'],
                        jsonargs['maxY'],
                        render=r)
        createlayer_fromtilespecs(EMtilespecs, outfile,0,shiftx=-jsonargs['minX'],shifty=-jsonargs['minY'])
        LMtilespecs = renderapi.tilespec.get_tile_specs_from_minmax_box(
                        LMstack,
                        z,
                        jsonargs['minX'],
                        jsonargs['maxX'],
                        jsonargs['minY'],
                        jsonargs['maxY'],
                        render=r)
        createlayer_fromtilespecs(LMtilespecs, outfile,1,shiftx=-jsonargs['minX'],shifty=-jsonargs['minY'],affineOnly=True)
        createfooters(outfile)

