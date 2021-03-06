import renderapi
import numpy as np
from functools import partial
import logging
from renderapi.transform import AffineModel, RigidModel
from ..module.render_module import RenderModule, RenderParameters
from argschema.fields import Str, Int, Boolean, InputFile
import marshmallow as mm
import json

example_json = {
    "render": {
        "host": "ibs-forrestc-ux1",
        "port": 8988,
        "owner": "Forrest",
        "project": "M246930_Scnn1a_4_f1",
        "client_scripts": "/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    "tile_pair_file": "/nas/data/M246930_Scnn1a_4_f1/processed/tilepairfiles/REG_DAPI1_DAPI2_tilepairs.json",
    "matchcollection": "M246930_Scnn1a_4_f1_DAPI2_TO_DAPI1",
    "local_transforms": 0
}


class MakeSyntheticCrossStackPointMatchesParameters(RenderParameters):
    tile_pair_file = InputFile(required=True,
                                description= 'tile pair file that has which tiles between src and dst should be connected')
    pool_size = Int(required=False, default=20,
                    description= 'degree of parallelism (default 20)')
    grid_size = Int(required=False,default =8,
                    description = 'number of points in one axis of grid points')
    matchcollection = Str(required=True, 
                          description= 'match collection to save point matches into')
    local_transforms = Int(required=False,default=0,description='how many transforms are local and the point matches should be written down in coordinates after this local transform is applied')

def define_local_grid(ts, num_points):
    xvals = np.linspace(0, ts.width - 1, num=num_points, endpoint=True, dtype=np.float64)
    yvals = np.linspace(0, ts.height - 1, num=num_points, endpoint=True, dtype=np.float64)
    (xx, yy) = np.meshgrid(xvals, yvals)
    # unravel the grid and make it a Nx2 matrix of x,y columns
    xy = np.vstack([xx.ravel(), yy.ravel()]).T
    return xy

def define_synthetic_point_matches(tsp,tsq,grid_size=8,local_transforms=0):
    src_points = define_local_grid(tsp,grid_size)
    src_points_global = renderapi.transform.estimate_dstpts(tsp.tforms,src_points)

    if local_transforms>0:
        src_points = renderapi.transform.estimate_dstpts(tsp.tforms[0:local_transforms],
                                                                    src_points)
    dst_points = src_points_global
    for tform in reversed(tsq.tforms[local_transforms:]):
        dst_points = tform.inverse_tform(dst_points)
    good_xmin=dst_points[:,0]>0
    good_ymin=dst_points[:,1]>0
    good_xmax=dst_points[:,0]<tsq.width
    good_ymax=dst_points[:,1]<tsq.height

    all_good =(good_xmin)&(good_ymin)&(good_xmax)&(good_ymax)
    dst_points = dst_points[all_good,:]
    src_points = src_points[all_good,:]
    match = {}
    match['pId']=tsp.tileId
    match['qId']=tsq.tileId
    match['pGroupId']=tsp.layout.sectionId
    match['qGroupId']=tsq.layout.sectionId
    match['matches']={
        'p':src_points.T.tolist(),
        'q':dst_points.T.tolist(),
        'w':np.ones(len(src_points)).tolist()
    }
    return match

def make_synthetic_cross_stack_point_matches(render,
                                             p_stack,
                                             q_stack,
                                             pairs,
                                             matchcollection,
                                             grid_size=8,
                                             local_transforms=0):

    for pair in pairs:
        tsp = renderapi.tilespec.get_tile_spec(p_stack, pair['p']['id'], render=render)
        tsq = renderapi.tilespec.get_tile_spec(q_stack, pair['q']['id'], render=render)
        match = define_synthetic_point_matches(tsp,tsq,grid_size,local_transforms)
#         src_points = define_local_grid(tsp,grid_size)
#         src_points_global = renderapi.transform.estimate_dstpts(tsp.tforms,src_points)

#         if local_transforms>0:
#             src_points = renderapi.transform.estimate_dstpts(tsp.tforms[0:local_transforms],
#                                                                         src_points)
#         dst_points = src_points_global
#         for tform in reversed(tsq.tforms[local_transforms:]):
#             dst_points = tform.inverse_tform(dst_points)
#         good_xmin=dst_points[:,0]>0
#         good_ymin=dst_points[:,1]>0
#         good_xmax=dst_points[:,0]<tsq.width
#         good_ymax=dst_points[:,1]<tsq.height

#         all_good =(good_xmin)&(good_ymin)&(good_xmax)&(good_ymax)
#         dst_points = dst_points[all_good,:]
#         src_points = src_points[all_good,:]

#         match = {}
#         match['pId']=pair['p']['id']
#         match['qId']=pair['q']['id']
#         match['pGroupId']=pair['p']['groupId']
#         match['qGroupId']=pair['q']['groupId']
#         match['matches']={
#             'p':src_points.T.tolist(),
#             'q':dst_points.T.tolist(),
#             'w':np.ones(len(src_points)).tolist()
#         }
        
        render.run(renderapi.pointmatch.import_matches,matchcollection,[match])

class MakeSyntheticCrossStackPointMatches(RenderModule):
    default_schema = MakeSyntheticCrossStackPointMatchesParameters

    def run(self):

        json_file = self.args['tile_pair_file']
        with open(json_file,'r') as fp:
            j = json.load(fp)
        p_stack = j['pstack']
        q_stack = j['qstack']
        pairs = j['neighborPairs']
        make_synthetic_cross_stack_point_matches(self.render,
                                             p_stack,
                                             q_stack,
                                             pairs,
                                             self.args['matchcollection'],
                                             self.args['grid_size'],
                                             self.args['local_transforms'])


if __name__ == "__main__":
    mod = MakeSyntheticCrossStackPointMatches(input_data=example_json)
    mod.run()
