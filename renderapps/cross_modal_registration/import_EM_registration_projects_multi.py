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

from ..module.render_module import TrakEM2RenderModule, EMLMRegistrationMultiParameters, RenderModule

import marshmallow as mm

example_json = {
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":8080,
        "owner":"Forrest",
        "project":"M247514_Rorb_1",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    "inputStack":"EM_Site4_stitched_SHIFT",
    "LMstacks":["BIGREG_MARCH_21_MBP_deconvnew"],
    "outputStack":"BIGREG_EM_Site4_stitched",
    "renderHome":"/var/www/render",
    "outputXMLdir":"/nas3/data/M247514_Rorb_1/processed/EMLMRegProjects_Site4/"
}
class ImportEMRegistrationMultiProjects(TrakEM2RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = EMLMRegistrationMultiParameters
        super(ImportEMRegistrationMultiProjects,self).__init__(schema_type=schema_type,*args,**kwargs)

    def run(self):
        print mod.args
        if not os.path.isdir(self.args['outputXMLdir']):
            os.makedirs(self.args['outputXMLdir'])
        xmlDir = self.args['outputXMLdir']
        #fill in missing bounds with the input stack bounds
        bounds = self.render.run(renderapi.stack.get_stack_bounds,self.args['inputStack'])
        for key in bounds.keys():
            self.args[key]=self.args.get(key,bounds[key])
        EMz = renderapi.stack.get_z_values_for_stack(self.args['inputStack'],render=self.render)

        tilespecsfiles = []

        buffersize = self.args['buffersize']
        self.args['minX'] = self.args['minX'] - buffersize
    	self.args['minY'] = self.args['minY'] - buffersize
    	self.args['maxX'] = self.args['maxX'] + buffersize
    	self.args['maxY'] = self.args['maxY'] + buffersize
        #width = self.args['maxX']-self.args['minX']
        #height = self.args['maxY']-self.args['minY']

        print("This is buffersize: %d "%buffersize)

        shiftTransform = AffineModel(B0=self.args['minX'] ,B1=self.args['minY'] )



        for z in EMz:
            infile = os.path.join(xmlDir,'%05d.xml'%z)
            outfile = os.path.join(xmlDir,'%05d.json'%z)
            newoutfile = os.path.join(xmlDir,'%05d-new.json'%z)
            self.convert_trakem2_project(infile,xmlDir,outfile)

            newtilejson = json.load(open(outfile,'r'))
            newEMtilespecs = [TileSpec(json=tsj) for tsj in newtilejson]
            EMtilespecs = renderapi.tilespec.get_tile_specs_from_minmax_box(
                            self.args['inputStack'],
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

        #renderapi.stack.delete_stack(self.args['outputStack'],render=self.render)
        sv = renderapi.stack.get_stack_metadata(self.args['inputStack'],render=self.render)
        renderapi.stack.create_stack(self.args['outputStack'],render=self.render)
        renderapi.stack.set_stack_metadata(self.args['outputStack'],sv,render=self.render)

        renderapi.client.import_jsonfiles_parallel(self.args['outputStack'],tilespecsfiles,render=self.render)

if __name__ == "__main__":
    mod = ImportEMRegistrationMultiProjects(input_data= example_json)
    mod.run()
