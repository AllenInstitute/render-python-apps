import renderapi
import renderapi.tilespec
from ..module.render_module import RenderModule, RenderParameters
from argschema.fields import Str

example_json={
        "render":{
            "host":"ibs-forrestc-ux1",
            "port":8080,
            "owner":"Forrest",
            "project":"M247514_Rorb_1",
            "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
        },
        "stack":"BIGALIGN2_MARCH24c_DAPI_1_deconvnew",
        "tileId":"tileid",
        "matchCollection":"mymatch collection"
}

class SplitTileParameters(RenderParameters):
    stack = Str(required=True,
        description='stack from tile to split')
    tileId = Str(required=True,
        description='tileId of tile to split')
    matchCollection = Str(required=True,
        description='matchCollection to base splitting on')

class SplitTile(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = SplitTileParameters
        super(SplitTile,self).__init__(schema_type=schema_type,*args,**kwargs)
    def run(self):
        self.logger.error('WARNING not complete')

        ts = renderapi.tilespec.get_tile_spec(self.args['stack'], self.args['tileId'])
        #pull the point matches that involve this tile out of the point match database
        section = ts.layout.sectionId
        matches = renderapi.pointmatch.get_matches_involving_tile(self.args['matchCollection'],
                                                        self.args['stack'],
                                                        self.args['tileId'])



if __name__ == "__main__":
    mod = SplitTile(input_data= example_json)
    mod.run()
