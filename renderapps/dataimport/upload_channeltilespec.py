from renderapi.transform  import AffineModel
from renderapi.tilespec import TileSpec,Layout
import numpy as np

import json
import glob
import renderapi
from ..module.render_module import RenderModule, RenderParameters
from sh import tar,zip


import marshmallow as mm

class UploadChannelTileSpecParameters(RenderParameters):
    inputDir = mm.fields.Str(required=True,
        metadata={'description':'directory to upload'})
    outputStack = mm.fields.Str(required=True,
        metadata={'description':'directory to upload'})
    channel = mm.fields.Str(required=True,
        metadata={'description':'directory to upload'})

class UploadChannelModule(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = UploadChannelTileSpecParameters
        super(UploadChannelModule,self).__init__(schema_type=schema_type,*args,**kwargs)
    def run(self):
        self.logger.error('NOT TESTED SPEAK TO FORREST IF WORKING OR NOT WORKING')

        print mod.args

        str = self.args['inputDir']+"/"+self.args['channel'] + "*.json"
        print str

        jsonfiles = sorted(glob.glob(str))
        print jsonfiles       
        renderapi.stack.create_stack(self.args['outputStack'],render=self.render)
        renderapi.client.import_jsonfiles_parallel(self.args['outputStack'],jsonfiles,render=self.render)


if __name__ == '__main__':
    mod = UploadChannelModule()
    mod.run()