import glob
import renderapi
from argschema.fields import InputDir, Str
from ..module.render_module import RenderModule, RenderParameters

class UploadTileSpecParameters(RenderParameters):
    inputDir = InputDir(required=True,
        metadata={'description':'input directory of tilespecs'})
    outputStack = Str(required=True,
        metadata={'description':'name of output stack to upload to render'})

class UploadTileSpecs(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = UploadTileSpecParameters
        super(UploadTileSpecs,self).__init__(schema_type=schema_type,*args,**kwargs)
    def run(self):
        self.logger.error('NOT TESTED SPEAK TO FORREST IF WORKING OR NOT WORKING')

        jsonfiles = sorted(glob.glob(self.args['inputDir']+"*.json"))
        print jsonfiles

        renderapi.stack.create_stack(self.args['outputStack'],render=self.render)
        renderapi.client.import_jsonfiles_parallel(self.args['outputStack'],jsonfiles,render=self.render)

if __name__ == "__main__":
    mod = UploadTileSpecs()
    mod.run()
