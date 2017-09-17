#!/usr/bin/env python
import os
#sys.path.insert(0,'/data/array_tomography/ImageProcessing/render-python/')
#sys.path.insert(0,'/nas3/data/M270907_Scnn1aTg2Tdt_13/scripts_ff/')
import renderapi
from ..TrakEM2.trakem2utils import (createchunks, createheader, createproject,
                                    createlayerset, createfooters,
                                    createlayer_fromtilespecs, Chunk)
from ..module.render_module import RenderModule, RenderParameters, TEM2ProjectTransfer
import numpy as np



example_parameters = {
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":8080,
        "owner":"KDM_SYN",
        "project":"KDM_SYN_100430B_L5",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    'minX':0,
    'maxX':1388,
    'minY':0,
    'maxY':1040,
    'minZ':0,
    'maxZ':48,
    'inputStack':'Stitched_YFP_1',
    'outputStack':'TEST',
    "doChunk":False,
    "outputXMLdir":"/nas4/KDM-SYN-100430B-L5_Deconv/Curated_SJS_2017/Deconvolved_and_Ultraligned/alignment_intermediates/trakem2/test",
    "renderHome":"/pipeline/forrestrender/"
}

class CreateTrakEM2Project(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = TEM2ProjectTransfer
        super(CreateTrakEM2Project,self).__init__(schema_type=schema_type,*args,**kwargs)
    def run(self):
        zvalues = self.render.run(renderapi.stack.get_z_values_for_stack,self.args['inputStack'])

        minZ = self.args.get('minZ',int(np.min(zvalues)))
        maxZ = self.args.get('maxZ',int(np.max(zvalues)))

        if self.args['doChunk']:
            allchunks = createchunks(minZ,maxZ,self.args['chunkSize'])
        else:
            allchunks=[]
            ck = Chunk()
            ck.first = minZ
            ck.last = maxZ
            ck.dir = str(ck.first)+ "-" + str(ck.last)
            allchunks.append(ck)

        layersetfile = "renderapps/TrakEM2/layerset.xml"
        headerfile = "renderapps/TrakEM2/header.xml"

        for x in allchunks:

            outdir = os.path.join(self.args['outputXMLdir'],x.dir)
            outfile=os.path.join(outdir,'project.xml')
            if not os.path.exists(outdir):
                os.makedirs(outdir)

            #copy header
            createheader(outfile)
            #create project
            createproject(outfile)
            #create layerset
            createlayerset(outfile,width=(self.args['maxX']-self.args['minX']),height=(self.args['maxY']-self.args['minY']))
            #add layers

            for layerid in range(x.first, x.last+1):
                print "This is layerid:"
                print layerid
                tilespecs = renderapi.tilespec.get_tile_specs_from_minmax_box(
                        self.args['inputStack'],
                        layerid,
                        self.args['minX'],
                        self.args['maxX'],
                        self.args['minY'],
                        self.args['maxY'],
                        render=self.render)
                print "Now adding layer: %d \n %d tiles"%(layerid,len(tilespecs))
                createlayer_fromtilespecs(tilespecs, outfile,layerid,shiftx=-self.args['minX'],shifty=-self.args['minY'])

            #footers
            print outfile
            createfooters(outfile)

if __name__ == "__main__":
    mod = CreateTrakEM2Project(input_data= example_parameters)
    mod.run()
