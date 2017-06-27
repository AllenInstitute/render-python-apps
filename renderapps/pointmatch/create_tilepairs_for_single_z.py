import numpy as np
from renderapi.transform import AffineModel
import renderapi
import json
import os
from functools import partial
import numpy as np
import time
import subprocess
from ..module.render_module import RenderModule,RenderParameters
import marshmallow as mm

example_parameters={
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":8080,
        "owner":"Forrest",
        "project":"M247514_Rorb_1",
        "client_scripts":"/var/www/render/render-ws-java-client/src/main/scripts"
    },
    "stack":"Rough_Aligned_68_to_112_DAPI_1",
    "tilepair_output":"/nas4/data/S3_Run1_Jarvis/processed/tilepairfiles1/tilepairs-z{z}-dz{dz}.json",
    "queryParameters":{
        "removeAllOption":"True",
        "minIntensity":0,
        "maxIntensity":655000
    }
    "z":0,
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
    radius = mm.fields.Float(required=False,default=.1,
        metadata={'description':'fraction of tile radius to look for pairs'})
    pool_size = mm.fields.Int(required=False,default=20,
        metadata={'description':'number of parallel processes (default 20)'})
    queryParameters = mm.fields.Nested(queryParameters,required=False,
        metadata={'description':'extra query parameters to add on to tilepair file if you have it'})


class Tile(mm.Schema):
    groupId = mm.fields.Str(required=True)
    id = mm.fields.Str(required=True)
class TilePair(mm.Schema):
    p = mm.fields.Nested(Tile, required=True)
    q = mm.fields.Nested(Tile, required=True)
class TilePairFile(mm.Schema):
    renderParametersUrlTemplate = mm.fields.Str(required=True)
    neighborPairs = mm.fields.List(TilePair)

def find_tile_pairs_in_radius(render,ts,z,dz,radius):
    pairs = []
    width = ts.width*(1+2*radius)
    height = ts.height(1+2*radius)
    minx = ts.minx - ts.width*radius
    miny = tx.miny - ts.width*radius
    p = {}
    p['id']=ts.tileId
    p['groupId']=ts.layout.sectionId

    for z2 in range(z-dz,z+dz+1):
        if (z!=z2):
            paired = render.run(renderapi.stack.get_tile_specs_from_box,stack,z,minx,miny,width,height)
            for ts2 in paired:
                q = {}
                q['id']=ts2.tileId
                q['groupId']=ts2.layout.sectionId
                pair = {'p':p,'q':q}
                pairs.append(pair)

    return pairs

def create_tile_pair_for_single_z(render,stack,z,dz=10,radius=.1,pool_size=20):
    tilespecs = render.run(renderapi.stack.get_tile_specs_from_z,stack,z)
    
    pairs = []
    for ts in tilespecs:
        pairs.append(find_tile_pairs_in_radius(render,ts,z,dz,radius))
    
    pairfile = {}
    pairfile['renderParametersUrlTemplate'] = 
    pairfile['neighborPairs']=pairs

    return pairfile
    
class CreateTilePairsForSingleZ(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = CreateTilePairsForSingleZParameters
        super(CreateTilePairsForSingleZ,self).__init__(schema_type=schema_type,*args,**kwargs)
    def run(self):
        
        tile_pair_json = create_tile_pair_for_single_z(self.render,
                                                       self.args['stack'],
                                                       self.args['z'],
                                                       self.args['dz'],
                                                       self.args['radius'],
                                                       self.args['pool_size'])
        
        tilepair_output = self.args['tilepair_output'].replace('{z}','%d'%z).replace('{dz}'%dz)
        with open(tilepair_output,'w') as fp:
            json.dump(tile_pair_json,fp)
        
if __name__ == "__main__":
    mod = CreateTilePairsForSingleZ(input_data=example_parameters)
    mod.run()
