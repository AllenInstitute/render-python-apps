from .create_tilepairs_for_single_z import CreateTilePairsForSingleZParameters as CreateTilePairsAcrossZBreakParameters
from tilepairs import create_tile_pair_across_z_break
from ..module.render_module import RenderModule,RenderParameters
import json

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
    "z":187,
    "dz":10,
    "radius":.1
}

class CreateTilePairsAcrossZBreak(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = CreateTilePairsAcrossZBreakParameters
        super(CreateTilePairsAcrossZBreak,self).__init__(schema_type=schema_type,*args,**kwargs)
    def run(self):
        
        qp=self.args.get('queryParameters',{})

        tile_pair_json = create_tile_pair_across_z_break(self.render,
                                                       self.args['stack'],
                                                       self.args['z'],
                                                       self.args['dz'],
                                                       self.args['radius'],
                                                       self.args['pool_size'],
                                                       qp,
                                                       self.args['overlap_frac'])

        with open(self.args['tilepair_output'],'w') as fp:
            json.dump(tile_pair_json,fp)
        
if __name__ == "__main__":
    mod = CreateTilePairsAcrossZBreak(input_data=example_parameters)
    mod.run()

