import renderapi
from renderapps.TrakEM2.trakem2utils import \
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = "import xml files for each Z to register EM to LM")
    parser.add_argument('--inputJson',help='json based input argument file',type=str)
    parser.add_argument('--verbose','-v',help='verbose logging',action='store_true')
    args = parser.parse_args()

    jsonargs = json.load(open(args.inputJson,'r'))
   
    if not os.path.isdir(jsonargs['outputXMLdir']):
        os.makedirs(jsonargs['outputXMLdir'])
    xmlDir = jsonargs['outputXMLdir']

    r=renderapi.render.connect(**jsonargs['render'])
    EMz = renderapi.stack.get_z_values_for_stack(jsonargs['EMstack'],render=r)

    renderAppDir= os.path.join(jsonargs['renderHome'],'render-app','target')
    renderJar = next(os.path.join(renderAppDir,f) for f in os.listdir(renderAppDir) if (f.startswith('render-app') and f.endswith('jar-with-dependencies.jar')))
    print renderJar

    if args.verbose:
        stripLogger(logging.getLogger())
        logging.basicConfig(level=logging.DEBUG,stream=sys.stdout)
        logging.debug('verbose mode enabled!')

    tilespecsfiles = []
    shiftTransform = AffineModel(B0=args['minX'],B1=args['minY'])

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
                        jsonargs['minX'],
                        jsonargs['maxX'],
                        jsonargs['minY'],
                        jsonargs['maxY'],
                        render=r)
        for ts in EMtilespecs:
            nts = next(t for t in newEMtilespecs if t.tileId == ts.tileId )
            ts.tforms=nts.tforms
            ts.tforms.append(shiftTransform)
        tilespecsfiles.append(newoutfile)
        renderapi.utils.renderdump(EMtilespecs,open(newoutfile,'w'))

    renderapi.stack.delete_stack(jsonargs['outputEMStack'],render=r)
    renderapi.stack.create_stack(jsonargs['outputEMStack'],render=r)
    renderapi.client.import_jsonfiles_parallel(jsonargs['outputEMStack'],tilespecsfiles,render=r)
