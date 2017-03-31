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

example_json = {
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":8080,
        "owner":"Forrest",
        "project":"M247514_Rorb_1",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    "inputStack":"EM_fix_stitch3",
    "LMstack":"REGFLATMBP_deconv",
    "outputStack":"EM_reg2",
    "renderHome":"/pipeline/render",
    "minX":190000,
    "minY":90000,
    "maxX":225424,
    "maxY":123142,
    "minZ":0,
    "maxZ":50,
    "outputXMLdir":"/nas3/data/M247514_Rorb_1/processed/EMLMRegProjects/"
}

class makeEMLMRegistrationProjects(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = EMLMRegistrationParameters
        super(makeEMLMRegistrationProjects,self).__init__(schema_type=schema_type,*args,**kwargs)
    def run(self):
        print self.args
        self.logger.error('WARNING NEEDS TO BE TESTED, TALK TO FORREST IF BROKEN')
    
        #fill in missing bounds with the input stack bounds
        bounds = self.render.run(renderapi.stack.get_stack_bounds,self.args['inputStack'])
        for key in bounds.keys():
            self.args[key]=self.args.get(key,bounds[key])

        if not os.path.isdir(self.args['outputXMLdir']):
            os.makedirs(self.args['outputXMLdir'])
        EMstack = self.args['inputStack']
        LMstack = self.args['LMstack']

        EMz = renderapi.stack.get_z_values_for_stack(self.args['inputStack'],render=self.render)

        layersetfile = "layerset.xml"
        headerfile = "header.xml"

        for z in EMz:
            outfile = os.path.join(self.args['outputXMLdir'],'%05d.xml'%z)
            createheader(headerfile,outfile)
            createproject(outfile)
            createlayerset(outfile,width=(self.args['maxX']-self.args['minX']),height=(self.args['maxY']-self.args['minY']))
            EMtilespecs = renderapi.tilespec.get_tile_specs_from_minmax_box(
                            EMstack,
                            z,
                            self.args['minX'],
                            self.args['maxX'],
                            self.args['minY'],
                            self.args['maxY'],
                            render=self.render)
            createlayer_fromtilespecs(EMtilespecs, outfile,0,shiftx=-self.args['minX'],shifty=-self.args['minY'])
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


if __name__ == "__main__":
    mod = makeEMLMRegistrationProjects(input_data= example_json)
    mod.run()

