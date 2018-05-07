import numpy as np
import renderapi
import json
import numpy as np
from ..module.render_module import RenderModule, RenderParameters
from ..shapely import tilespec_to_bounding_box_polygon
import argschema
import os

example_parameters={
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":8080,
        "owner":"Forrest",
        "project":"M247514_Rorb_1",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    "ref_stack":"LENS_DAPI_1_deconvnew",
    "stack":"LENS_DAPI_2_deconvnew",
    "tilepair_output":"/nas3/data/M247514_Rorb_1/processed/tilepairfiles/LENS_DAPI1_DAPI2_tilepairs.json"
}

class FindPrincipalTileOverlapParameters(RenderParameters):
    ref_stack = argschema.fields.Str(required=True,
        description="stack to search within for principal overlapping tile")
    stack = argschema.fields.Str(required=True,
        description='lookup principal overlap tile in ref_stack for each tile in this stack')
    tilepair_output = argschema.fields.Str(required=True,
        metadata = {'description':'path to save tilepair file output'})
    pool_size = argschema.fields.Int(required=False,default=20,
        description='number of parallel processes (default 20)')

class Tile(argschema.schemas.mm.Schema):
    groupId = argschema.fields.Str(required=True)
    id = argschema.fields.Str(required=True)
class TilePair(argschema.schemas.mm.Schema):
    p = argschema.fields.Nested(Tile, required=True)
    q = argschema.fields.Nested(Tile, required=True)
class CrossStackTilePairFile(argschema.schemas.mm.Schema):
    pstack = argschema.fields.Str(required=True)
    qstack = argschema.fields.Str(required=True)
    neighborPairs = argschema.fields.Nested(TilePair,many=True)

def find_tile_pair(render,stack,ts,ref_stack):
 
    ts_geom = tilespec_to_bounding_box_polygon(ts)

    width = ts.width
    height = ts.height
    minx = ts.minX
    miny = ts.minY
    p = {}
    p['id']=ts.tileId
    p['groupId']=ts.layout.sectionId

    paired = render.run(renderapi.tilespec.get_tile_specs_from_box,ref_stack,ts.z,minx,miny,width,height)
    overlap_tuples = []
    for ts2 in paired:
        ts2_geom = tilespec_to_bounding_box_polygon(ts2)
        overlap = ts_geom.intersection(ts2_geom)
        frac_overlap = overlap.area/ts_geom.area
        overlap_tuples.append((ts2,frac_overlap))
    sorted_overlaps_tuples = sorted(overlap_tuples,key= lambda x: x[1])
    #print ts.tileId,sorted_overlaps_tuples[0][1],sorted_overlaps_tuples[-1][1]
    ts2 = sorted_overlaps_tuples[-1][0]
    q = {}
    q['id']=ts2.tileId
    q['groupId']=ts2.layout.sectionId
    pair = {'p':p,'q':q}
    #print sorted_overlaps_tuples,ts2.tileId,ts.tileId
    return pair

def create_principal_overlap_tile_pair(render,stack,ref_stack,pool_size=20,queryParameters={}):
    tilespecs = render.run(renderapi.tilespec.get_tile_specs_from_stack ,stack)

    pairs = []
    for ts in tilespecs:
        pairs.append(find_tile_pair(render,stack,ts,ref_stack))
        #break
    pairfile = {}
   
    pairfile['pstack'] = stack
    pairfile['qstack'] = ref_stack
    pairfile['neighborPairs']=pairs

    return pairfile

class FindPrincipalTileOverlap(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = FindPrincipalTileOverlapParameters
        super(FindPrincipalTileOverlap,self).__init__(schema_type=schema_type,*args,**kwargs)
    def run(self):

        qp=self.args.get('queryParameters',{})

        tile_pair_json = create_principal_overlap_tile_pair(self.render,
                                                       self.args['stack'],
                                                       self.args['ref_stack'],
                                                       pool_size=self.args['pool_size'],
                                                       queryParameters=qp)
        outfilepath =self.args['tilepair_output']
        
        with open(outfilepath,'w') as fp:
            json.dump(tile_pair_json,fp)

if __name__ == "__main__":
    mod = FindPrincipalTileOverlap(input_data=example_parameters)
    mod.run()
