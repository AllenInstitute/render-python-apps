import renderapi
from renderapps.TrakEM2.trakem2utils import createchunks,createheader,createproject,createlayerset,createfooters,createlayer_fromtilespecs,Chunk
import json
import logging
import os
import sys
from renderapi.utils import stripLogger
import argparse
from renderapps.module.render_module import TrakEM2RenderModule, RenderParameters, EMLMRegistrationParameters
import marshmallow as mm

if __name__ == '__main__':

    mod = TrakEM2RenderModule(schema_type = EMLMRegistrationParameters)
    
    #fill in missing bounds with the input stack bounds
    bounds = mod.render.run(renderapi.stack.get_stack_bounds,mod.args['inputStack'])
    for key in bounds.keys():
        mod.args[key]=mod.args.get(key,bounds[key])

    if not os.path.isdir(mod.args['outputXMLdir']):
        os.makedirs(mod.args['outputXMLdir'])
    EMstack = mod.args['inputStack']
    LMstack = mod.args['LMstack']

    EMz = renderapi.stack.get_z_values_for_stack(mod.args['inputStack'],render=mod.render)

    layersetfile = "layerset.xml"
    headerfile = "header.xml"

    for z in EMz:
        outfile = os.path.join(mod.args['outputXMLdir'],'%05d.xml'%z)
        createheader(headerfile,outfile)
        createproject(outfile)
        createlayerset(outfile,width=(mod.args['maxX']-mod.args['minX']),height=(mod.args['maxY']-mod.args['minY']))
        EMtilespecs = renderapi.tilespec.get_tile_specs_from_minmax_box(
                        EMstack,
                        z,
                        mod.args['minX'],
                        mod.args['maxX'],
                        mod.args['minY'],
                        mod.args['maxY'],
                        render=mod.render)
        createlayer_fromtilespecs(EMtilespecs, outfile,0,shiftx=-mod.args['minX'],shifty=-mod.args['minY'])
        LMtilespecs = renderapi.tilespec.get_tile_specs_from_minmax_box(
                        LMstack,
                        z,
                        mod.args['minX'],
                        mod.args['maxX'],
                        mod.args['minY'],
                        mod.args['maxY'],
                        render=mod.render)
        createlayer_fromtilespecs(LMtilespecs, outfile,1,shiftx=-mod.args['minX'],shifty=-mod.args['minY'],affineOnly=True)
        createfooters(outfile)

