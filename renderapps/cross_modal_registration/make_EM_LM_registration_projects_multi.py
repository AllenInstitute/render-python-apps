import renderapi
from ..TrakEM2.trakem2utils import createchunks,createheader,createproject,createlayerset,createfooters,createlayer_fromtilespecs,Chunk
import json
import logging
import os
import sys
from renderapi.utils import stripLogger
import argparse
from ..module.render_module import TrakEM2RenderModule, RenderParameters, EMLMRegistrationMultiParameters, RenderModule
import marshmallow as mm

example_json = {
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":8080,
        "owner":"Forrest",
        "project":"M247514_Rorb_1",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    "inputStack":"BIGREG_EM_Site4_stitched",
    "LMstacks":["BIGREG_MARCH_21_PSD95","BIGREG_MARCH_21_MBP_deconvnew","BIGREG_MARCH_21_DAPI_1"],
    "outputStack":"BIGREG_EM_Site4",
    "renderHome":"/var/www/render",
    "outputXMLdir":"/nas3/data/M247514_Rorb_1/processed/EMLMRegMultiProjects_Site4b/"
}
class makeEMLMRegistrationMultiProjects(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = EMLMRegistrationMultiParameters
        super(makeEMLMRegistrationMultiProjects,self).__init__(schema_type=schema_type,*args,**kwargs)
    def run(self):
        print self.args
        
    
        #fill in missing bounds with the input stack bounds
        bounds = self.render.run(renderapi.stack.get_stack_bounds,self.args['inputStack'])
        for key in bounds.keys():
            self.args[key]=self.args.get(key,bounds[key])

        if not os.path.isdir(self.args['outputXMLdir']):
            os.makedirs(self.args['outputXMLdir'])
        EMstack = self.args['inputStack']
        LMstacks = self.args['LMstacks']

        EMz = renderapi.stack.get_z_values_for_stack(self.args['inputStack'],render=self.render)

        for z in EMz:
            outfile = os.path.join(self.args['outputXMLdir'],'%05d.xml'%z)
            createheader(outfile)
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
            for i,LMstack in enumerate(LMstacks):
                LMtilespecs = renderapi.tilespec.get_tile_specs_from_minmax_box(
                                LMstack,
                                z,
                                mod.args['minX'],
                                mod.args['maxX'],
                                mod.args['minY'],
                                mod.args['maxY'],
                                render=mod.render)
                if 'PSD' in LMstack:
                    for ts in LMtilespecs:
                        ts.minint = 2400
                        ts.maxint = 7000
                if 'MBP' in LMstack:
                    for ts in LMtilespecs:
                        ts.minint = 0
                        ts.maxint = 6000

                createlayer_fromtilespecs(LMtilespecs, outfile,i+1,shiftx=-mod.args['minX'],shifty=-mod.args['minY'],affineOnly=True)
            createfooters(outfile)

if __name__ == "__main__":
    mod = makeEMLMRegistrationMultiProjects(input_data= example_json)
    mod.run()

