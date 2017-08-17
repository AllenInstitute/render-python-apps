import renderapi
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from functools import partial
import pathos.multiprocessing as mp
from matplotlib.patches import FancyArrowPatch, Circle, ConnectionStyle
import os
from ..module.render_module import RenderModule, RenderParameters
from argschema.fields import InputFile, InputDir, Str, Int

parameters={
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":8080,
        "owner":"Forrest",
        "project":"M247514_Rorb_1",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    "stack":"BIGLENS_REG_MARCH_21_DAPI_1_deconvnew",
    "src_matchcollection":"M247514_Rorb_1_final_DAPI_filtered",
    "dst_matchcollection":"POSTLENS_M247514_Rorb_1_final_DAPI_filtered",
    "num_transforms":1,
}


class MapPointMatchForwardParameters(RenderParameters):
    stack = Str(required=True,
        description='stack to use to map point matches forward from root local, to a new space')
    src_matchcollection = Str(required=True,
        description='match collection to start with  to make point match plots')
    dst_matchcollection = Str(required=True,
        description='match collection to store results into')
    num_transforms = Int(required = False,
                         default=1,
                         description="how many transforms in stack to transform point matches forward through")
    pool_size = Int(required=False,default=20,
        description='number of parallel threads to use')

def process_group(render,
                  tilespecs,
                  psection,
                  src_matchcollection,
                  dst_matchcollection,
                  num_transforms=1):

    matches = render.run(renderapi.pointmatch.get_matches_with_group,src_matchcollection,psection)
    
    for match in matches:
        pxy = np.array(match['matches']['p'],dtype=np.float64).T
        qxy = np.array(match['matches']['q'],dtype=np.float64).T
        tsp = next(ts for ts in tilespecs if ts.tileId == match['pId'])
        tsq = next(ts for ts in tilespecs if ts.tileId == match['qId'])
        for i in range(num_transforms):
            ptform = tsp.tforms[i]
            pxy = ptform.tform(pxy)
            qtform = tsq.tforms[i]
            qxy = qtform.tform(qxy)
                        
        match['matches']['p']= pxy.T.tolist()
        match['matches']['q']= qxy.T.tolist()

    render.run(renderapi.pointmatch.import_matches,dst_matchcollection,matches)
                
def map_point_matches_forward(render,
                              src_matchcollection,
                              dst_matchcollection,
                              stack,
                              num_transforms=1,
                              pool_size=20):

    tilespecs = render.run(renderapi.tilespec.get_tile_specs_from_stack, stack)
    pgroups = render.run(renderapi.pointmatch.get_match_groupIds_from_only, src_matchcollection)
    for psection in pgroups:
        print psection
        process_group(render,
                      tilespecs,
                      psection,
                      src_matchcollection,
                      dst_matchcollection,
                      num_transforms=num_transforms)


class MapPointMatchForward(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = MapPointMatchForwardParameters
        super(MapPointMatchForward,self).__init__(schema_type=schema_type,*args,**kwargs)
    def run(self):
        self.logger.error("NEEDS TESTING.. TALK TO FORREST IF BROKEN OR WORKS")
        
        map_point_matches_forward(self.render,
                                  self.args['src_matchcollection'],
                                  self.args['dst_matchcollection'],
                                  self.args['stack'],
                                  self.args['num_transforms'],
                                  self.args['pool_size'])


if __name__ == "__main__":
    mod = MapPointMatchForward(input_data = parameters)
    mod.run()
