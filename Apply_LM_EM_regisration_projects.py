from RenderModule import RenderModule
import logging
import os
import renderapi
import json
import argparse
from renderapi.tilespec import TileSpec
from renderapi.transform import AffineModel

logger = logging.getLogger(__name__)

class ApplyLMEMRegistration(RenderModule):
    '''module to apply LM to EM transformations produced by make_EM_LM_registration_projects'''
    def __init__(self, parser, *args,**kwargs):

        RenderModule.__init__(self,parser,*args,**kwargs)

    def run(self):
        print 'running with'
        print json.dumps(self.args,indent=4)

        EMstack = self.args['EMstack']
        outstack = self.args['outputEMStack']
        xmlDir = self.args['outputXMLdir']
        #jsonargfile = '/nas3/data/M247514_Rorb_1/processed/TEMprojects/test_input_json.json'
        #args= json.load(open(jsonargfile,'r'))
        #outputJsonfile = '/nas3/data/M247514_Rorb_1/processed/TEMprojects/test_output_json.json'
        #jsonoutputargs = json.load(open(outputJsonfile,'r'))

        r=renderapi.render.connect(**self.args['render'])
        EMz = renderapi.stack.get_z_values_for_stack(EMstack,render=r)

        renderAppDir= os.path.join(self.args['renderHome'],'render-app','target')
        renderJar = [os.path.join(renderAppDir,f) for f in os.listdir(renderAppDir) if (f.startswith('render-app') and f.endswith('jar-with-dependencies.jar'))][0]
        logger.debug(renderJar)

        tilespecsfiles = []
        shiftTransform = AffineModel(B0=self.args['minX'],B1=self.args['minY'])

        for z in EMz:
            infile = os.path.join(xmlDir,'%05d.xml'%z)
            outfile = os.path.join(xmlDir,'%05d.json'%z)
            newoutfile = os.path.join(xmlDir,'%05d-new.json'%z)
            cmd = ['java','-cp',renderJar,'org.janelia.alignment.trakem2.Converter',infile,xmlDir,outfile]
            os.system(' '.join(cmd))
            newtilejson = json.load(open(outfile,'r'))
            newEMtilespecs = [TileSpec(json=tsj) for tsj in newtilejson]
            EMtilespecs = renderapi.tilespec.get_tile_specs_from_minmax_box(
                            EMstack,
                            z,
                            self.args['minX'],
                            self.args['maxX'],
                            self.args['minY'],
                            self.args['maxY'],
                            render=r)
            for ts in EMtilespecs:
                nts = next(t for t in newEMtilespecs if t.tileId == ts.tileId )
                ts.tforms=nts.tforms
                ts.tforms.append(shiftTransform)
            tilespecsfiles.append(newoutfile)
            renderapi.utils.renderdump(EMtilespecs,open(newoutfile,'w'),indent=4)

        renderapi.stack.delete_stack(outstack,render=r)
        renderapi.stack.create_stack(outstack,render=r)
        renderapi.client.import_jsonfiles_parallel(outstack,tilespecsfiles,render=r)

if __name__ == '__main__':

    p = argparse.ArgumentParser(description="Apply EM_LM trakem2 registration projects")
    example_json={
        "render":{
            "host":"ibs-forrestc-ux1",
            "port":8080,
            "owner":"Forrest",
            "project":"M247514_Rorb_1",
            "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
        },
        "EMstack":"EM_fix_stitch3",
        "LMstack":"REGFLATMBP_deconv",
        "outputEMStack":"EM_reg2",
        "renderHome":"/pipeline/render",
        "minX":190000,
        "minY":90000,
        "maxX":225424,
        "maxY":123142,
        "minZ":0,
        "maxZ":50,
        "outputXMLdir":"/nas3/data/M247514_Rorb_1/processed/EMLMRegProjects/"
    }

    module = ApplyLMEMRegistration(p,example_json=example_json)
    module.run()

