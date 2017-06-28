import json
from ..module.render_module import RenderModule,RenderParameters
import marshmallow as mm
from tilepairs import create_tile_pair_for_single_z

example_parameters={
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":8080,
        "owner":"S3_Run1",
        "project":"S3_Run1_Jarvis",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    "stack":"Rough_Aligned_68_to_112_DAPI_1_fullscale_CONS",
    "tilepair_output":"/nas4/data/S3_Run1_Jarvis/processed/tilepairfiles1/tilepairs-z315-dz10.json",
    "queryParameters":{
        "removeAllOption":"true",
        "minIntensity":0,
        "maxIntensity":65500
    },
    "z":315,
    "dz":10,
    "radius":.1
}
class queryParameters(mm.Schema):
    removeAllOption = mm.fields.Boolean(required=False,
        metadata={'description':'boolean to include as to whether to strip all transforms when rendering for normalizeForMatching=true'})
    minIntensity = mm.fields.Int(required=False,
        metadata={'description':'option to override minIntensity settings of each tilespec to this value'})
    maxIntensity = mm.fields.Int(required=False,
        metadata={'description':'option to override maxIntensity settings of each tilespec to this value'})

class CreateTilePairsForSingleZParameters(RenderParameters):
    stack = mm.fields.Str(required=True,
        metadata={'description':'stack to take stitching from'})
    z = mm.fields.Int(required=True,
        metadata={'description':'z value to create tilepairs that include'})
    dz = mm.fields.Int(required=False,default=10,
        metadata ={'description':'number of sections away to include in tilepair'})
    tilepair_output = mm.fields.Str(required=True,
        metadata = {'description':'path to save tilepair file output'})
    radius = mm.fields.Float(required=False,default=.1,
        metadata={'description':'fraction of tile radius to look for pairs'})
    overlap_frac = mm.fields.Float(required=False,default=.25,
        metadata={'description':'fraction of tile area overlap necessary to include in pairfile'})
    pool_size = mm.fields.Int(required=False,default=20,
        metadata={'description':'number of parallel processes (default 20)'})
    queryParameters = mm.fields.Nested(queryParameters,required=False,
        metadata={'description':'extra query parameters to add on to tilepair file if you have it'})
    
class CreateTilePairsForSingleZ(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = CreateTilePairsForSingleZParameters
        super(CreateTilePairsForSingleZ,self).__init__(schema_type=schema_type,*args,**kwargs)
    def run(self):
        
        qp=self.args.get('queryParameters',{})

        tile_pair_json = create_tile_pair_for_single_z(self.render,
                                                       self.args['stack'],
                                                       self.args['z'],
                                                       self.args['dz'],
                                                       self.args['radius'],
                                                       self.args['pool_size'],
                                                       qp,
                                                       overlap_frac=self.args['overlap_frac'])

        with open(self.args['tilepair_output'],'w') as fp:
            json.dump(tile_pair_json,fp)
        
if __name__ == "__main__":
    mod = CreateTilePairsForSingleZ(input_data=example_parameters)
    mod.run()
