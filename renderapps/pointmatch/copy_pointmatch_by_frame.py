import renderapi
import numpy as np
from functools import partial
import pathos.multiprocessing as mp
import os
from ..module.render_module import RenderModule, RenderParameters
from argschema.fields import InputFile, InputDir, Str, Int
import json


example_parameters={
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":80,
        "owner":"S3_Run1",
        "project":"S3_Run1_Jarvis",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    "input_matchcollection":"",
    "output_matchcollection":"",
    "input_stack":"",
    "output_stack":""
}


def find_corresponding_tile(render,section,input_id,input_stack,output_stack):
    input_tilespec = render.run(renderapi.tilespec.get_tile_spec,intput_stack,input_id)
    z = render.run(renderapi.stack.get_z_value_for_section,output_stack,section)
    output_tilespecs = render.run(renderapi.tilespec.get_tile_specs_from_z,output_stack,z)

    for ts in output_tilespecs:
        tilediff = int(input_tilespec.tileId)-int(ts.tileId)
        if np.abs(tilediff)<10:
            return ts.tileId

def copy_point_matches_by_frame(render,
                                input_matchcollection,
                                output_matchcollection,
                                input_stack,
                                output_stack,
                                pool_size=20):
    pgroups = render.run(renderapi.pointmatch.get_match_groupIds_from_only, input_matchcollection)
    for psection in pgroups:
        matches = render.run(renderapi.pointmatch.get_matches_with_group, psection)
        match0 = matches[0]
        qsection = match0['qGroupId']
        pid = match0['pid']
        qid = match0['qid']
        pid2 = find_corresponding_tile(render, psection, pid, input_stack, output_stack)
        deltId = int(pid2)-int(pid)

        for match in matches:
            match['pid']=str(int(match['pid'])+deltId)
            match['qid']=str(int(match['qid'])+deltId)
        render.run(renderapi.pointmatch.import_matches,output_matchcollection,matches)


class CopyPointMatchesByFrameParameters(RenderParameters):
    input_matchcollection = Str(required=True,
        description='match collection to copy point matches from')
    output_matchcollection = Str(required=True,
        description='match collection to copy point matches to')
    input_stack = Str(required=True,
        description='stack with tiles that input_matchcollection came from')
    output_stack = Str(required=True,
        description='stack with tiles that you want to save point matches into\
        matching on the frame number (array tomography specific)')
    pool_size = Int(required=False,default=20,
        description='number of parallel threads to use')

class CopyPointMatchesByFrame(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = CopyPointMatchesByFrameParameters
        super(CopyPointMatchesByFrame,self).__init__(schema_type=schema_type,*args,**kwargs)

    def run(self):
        copy_point_matches_by_frame(self.render,
            self.args['input_matchcollection'],
            self.args['output_matchcollection'],
            self.args['input_stack'],
            self.args['output_stack'],
            self.args['pool_size'])

if __name__ == "__main__":
    mod = CopyPointMatchesByFrame(input_data = example_parameters)
    mod.run()
