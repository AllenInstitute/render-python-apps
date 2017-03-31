import renderapi
from ..TrakEM2.trakem2utils import \
    createchunks, createheader, createproject, \
    createlayerset, createfooters, createlayer_fromtilespecs, Chunk
import json
import logging
import os
import sys
from renderapi.utils import stripLogger
import argparse
from renderapi.tilespec import TileSpec
from renderapi.transform import AffineModel
import json
from ..module.render_module import TrakEM2RenderModule, EMLMRegistrationParameters

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
class ImportEMRegistrationProjects(TrakEM2RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = EMLMRegistrationParameters
        super(Template,self).__init__(schema_type=schema_type,*args,**kwargs)

    def run(self):
        print mod.args
        self.logger.error('WARNING NEEDS TO BE TESTED, TALK TO FORREST IF BROKEN')
        if not os.path.isdir(self.args['outputXMLdir']):
            os.makedirs(self.args['outputXMLdir'])
        xmlDir = self.args['outputXMLdir']

        EMz = renderapi.stack.get_z_values_for_stack(self.args['EMstack'],render=self.render)

        tilespecsfiles = []
        shiftTransform = AffineModel(B0=args['minX'],B1=args['minY'])

        for z in EMz:
            infile = os.path.join(xmlDir,'%05d.xml'%z)
            outfile = os.path.join(xmlDir,'%05d.json'%z)
            newoutfile = os.path.join(xmlDir,'%05d-new.json'%z)
            self.convert_trakem2_project(self,infile,xmlDir,outfile)
         
            newtilejson = json.load(open(outfile,'r'))
            newEMtilespecs = [TileSpec(json=tsj) for tsj in newtilejson]
            EMtilespecs = renderapi.tilespec.get_tile_specs_from_minmax_box(
                            EMstack,
                            z,
                            self.args['minX'],
                            self.args['maxX'],
                            self.args['minY'],
                            self.args['maxY'],
                            render=self.render)
            for ts in EMtilespecs:
                nts = next(t for t in newEMtilespecs if t.tileId == ts.tileId )
                ts.tforms=nts.tforms
                ts.tforms.append(shiftTransform)
            tilespecsfiles.append(newoutfile)
            renderapi.utils.renderdump(EMtilespecs,open(newoutfile,'w'))

        renderapi.stack.delete_stack(self.args['outputEMStack'],render=self.render)
        renderapi.stack.create_stack(self.args['outputEMStack'],render=self.render)
        renderapi.client.import_jsonfiles_parallel(self.args['outputEMStack'],tilespecsfiles,render=self.render)

if __name__ == "__main__":
    mod = ImportEMRegistrationProjects(input_data= example_json)
    mod.run()