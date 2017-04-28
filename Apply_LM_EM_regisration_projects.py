from render_module import TrakEM2RenderModule,EMLMRegistrationParameters
import os
import renderapi
import json
from renderapi.tilespec import TileSpec
from renderapi.transform import AffineModel

example_json={
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


if __name__ == '__main__':
    mod = TrakEM2RenderModule(schema_type = EMLMRegistrationParameters,input_data=example_json)

    EMstack = mod.args['inputStack']
    outstack = mod.args['outputStack']
    xmlDir = mod.args['outputXMLdir']
    #jsonargfile = '/nas3/data/M247514_Rorb_1/processed/TEMprojects/test_input_json.json'
    #args= json.load(open(jsonargfile,'r'))
    #outputJsonfile = '/nas3/data/M247514_Rorb_1/processed/TEMprojects/test_output_json.json'
    #jsonoutputargs = json.load(open(outputJsonfile,'r'))

    r=mod.render
    EMz = renderapi.stack.get_z_values_for_stack(EMstack,render=r)
    
    renderJar = mod.renderJar
    mod.logger.debug(renderJar)

    tilespecsfiles = []
    shiftTransform = AffineModel(B0=mod.args['minX'],B1=mod.args['minY'])

    for z in EMz:
        infile = os.path.join(xmlDir,'%05d.xml'%z)
        outfile = os.path.join(xmlDir,'%05d.json'%z)
        newoutfile = os.path.join(xmlDir,'%05d-new.json'%z)
        mod.convert_trakem2_project(infile,xmlDir,outfile)
        newtilejson = json.load(open(outfile,'r'))
        newEMtilespecs = [TileSpec(json=tsj) for tsj in newtilejson]
        EMtilespecs = renderapi.tilespec.get_tile_specs_from_minmax_box(
                        EMstack,
                        z,
                        mod.args['minX'],
                        mod.args['maxX'],
                        mod.args['minY'],
                        mod.args['maxY'],
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

