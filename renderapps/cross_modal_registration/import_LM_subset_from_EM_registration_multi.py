if __name__ == "__main__" and __package__ is None:
    __package__ = "renderapps.cross_modal_registration.import_LM_subset_from_EM_registration_multi"

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
import argschema

from ..module.render_module import TrakEM2RenderModule, EMLMRegistrationMultiParameters, RenderModule

import marshmallow as mm

example_json =   {
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":8080,
        "owner":"Forrest",
        "project":"M247514_Rorb_1",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    "inputStack":"BIGREG_EMTake2Site3",
    "LMstacks":["BIGREG_MARCH_21_PSD95","BIGREG_MARCH_21_MBP_deconvnew","BIGREG_MARCH_21_DAPI_1"],
    "LMstack_index":0,
    "outputStack":"subsetTake2Site3BIGREG_MARCH_21_PSD95",
    "renderHome":"/var/www/render",
    "outputXMLdir":"/nas3/data/M247514_Rorb_1/processed/EMLMRegMultiProjects_Take2Site3_apply/"
}

class ImportLMSubsetFromEMRegistrationMultiProjectsParameters(EMLMRegistrationMultiParameters):
    LMstack_index = argschema.fields.Int(required=True, default =0,description="which LMstack to import")
    
class ImportLMSubsetFromEMRegistrationMultiProjects(TrakEM2RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = ImportLMSubsetFromEMRegistrationMultiProjectsParameters
        super(ImportLMSubsetFromEMRegistrationMultiProjects,self).__init__(schema_type=schema_type,*args,**kwargs)

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
        lmstack = self.args['LMstacks'][self.args['LMstack_index']]

        for z in EMz:
            infile = os.path.join(xmlDir,'%05d.xml'%z)
            outfile = os.path.join(xmlDir,'%05d.json'%z)
            newoutfile = os.path.join(xmlDir,'%05d-newLM.json'%z)
            self.convert_trakem2_project(infile,xmlDir,outfile)
         
            newtilejson = json.load(open(outfile,'r'))
            newtilespecs = [TileSpec(json=tsj) for tsj in newtilejson]
            LMtilespecs = renderapi.tilespec.get_tile_specs_from_z(
                            lmstack,
                            z,
                            render=self.render)
            LMtilespecssubset = []
            for ts in newtilespecs:
                try:
                    nts = next(t for t in LMtilespecs if t.tileId == ts.tileId )
                    print nts.tileId
                    LMtilespecssubset.append(nts)
                except:
                    pass

            tilespecsfiles.append(newoutfile)
            with open(newoutfile,'w') as fp:
                renderapi.utils.renderdump(LMtilespecssubset,fp)

        #renderapi.stack.delete_stack(self.args['outputStack'],render=self.render)
        sv = renderapi.stack.get_stack_metadata(lmstack,render=self.render)
        renderapi.stack.create_stack(self.args['outputStack'],render=self.render)
        renderapi.stack.set_stack_metadata(self.args['outputStack'],sv,render=self.render)

        renderapi.client.import_jsonfiles_parallel(self.args['outputStack'],tilespecsfiles,render=self.render)

if __name__ == "__main__":
    mod = ImportLMSubsetFromEMRegistrationMultiProjects(input_data= example_json)
    mod.run()