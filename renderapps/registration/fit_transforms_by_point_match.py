import renderapi
import numpy as np
from functools import partial
import logging
from renderapi.transform import AffineModel, RigidModel
from ..module.render_module import RenderModule, RenderParameters
from argschema.fields import Str, Int, Boolean
import marshmallow as mm

example_json = {
    "render": {
        "host": "ibs-forrestc-ux1",
        "port": 8080,
        "owner": "Forrest",
        "project": "M247514_Rorb_1",
        "client_scripts": "/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    "dst_stack": "LENS_REG_MARCH_21_DAPI_1_deconvnew",
    "src_stack": "LENS_DAPI_3_deconvnew",
    "output_stack": "testLENS_REG_MARCH_21_DAPI_3_deconvnew",
    "matchcollection": "POSTLENS_M247514_Rorb_1_DAPI3_TO_DAPI1",
    "num_local_transforms": 1,
    "transform_type": "rigid"
}


class FitTransformsByPointMatchParameters(RenderParameters):
    dst_stack = Str(required=True,
                               description= 'stack with tiles in the desired destination space')
    src_stack = Str(required=True,
                                description='stack with tiles in the input space')

    output_stack = Str(required=True,
                       description= 'name to call output version of \
                       input_stack_src_space with a transform added to bring it \
                       into the destination space')

    matchcollection = Str(required=True,
                            description = "point match collection expressing point matches between the stacks")

    num_local_transforms = Int(required=True,
                               description="number of local transforms to preserver, \
                               assumes point matches written down after such local transforms")
    transform_type = Str(required = False, default = 'affine',
                         validate = mm.validate.OneOf(["affine","rigid"]),
                         description = "type of transformation to fit")
    pool_size = Int(required=False, default=20,
                    description= 'degree of parallelism (default 20)')
   
logger = logging.getLogger(__name__)

def fit_transforms_by_pointmatch(render,
                                 src_stack,
                                 dst_stack,
                                 matchcollection,
                                 num_local_transforms,
                                 Transform):
    print src_stack,dst_stack,matchcollection,num_local_transforms
    tilespecs_p = renderapi.tilespec.get_tile_specs_from_stack(src_stack, render=render)
    tilespecs_q = renderapi.tilespec.get_tile_specs_from_stack(dst_stack, render=render)

    tilespecs_out = []
    for k,tsp in enumerate(tilespecs_p):
        pid=tsp.tileId
        pgroup = tsp.layout.sectionId
        try:
            match = renderapi.pointmatch.get_matches_involving_tile(matchcollection,pgroup,pid,render=render)[0]
            if match['qId']==pid:
                pid = match['qId']
                qid = match['pId']
                p_pts = np.array(match['matches']['q']).T
                q_pts = np.array(match['matches']['p']).T
            else:
                pid = match['pId']
                qid = match['qId']
                p_pts = np.array(match['matches']['p']).T
                q_pts = np.array(match['matches']['q']).T
            
            tsq = next(ts for ts in tilespecs_q if ts.tileId == qid)
            tforms = tsq.tforms[num_local_transforms:]
            dst_pts = renderapi.transform.estimate_dstpts(tforms,q_pts)
            p_pts_global = renderapi.transform.estimate_dstpts(tsp.tforms[num_local_transforms:],p_pts)
            final_tform = Transform()
            final_tform.estimate(p_pts,dst_pts)
            tsp.tforms=tsp.tforms[0:num_local_transforms]+[final_tform]
            tilespecs_out.append(tsp)
        except IndexError as e:
            pass
        except StopIteration as e:
            pass
        # print pid,qid
        # print "p_pts"
        # print p_pts
        # print "dst_pts"
        # print dst_pts
        # print "p_pts_global"
        # print p_pts_global
        # if k==1:
        #     break

    return tilespecs_out


class FitTransformsByPointMatch(RenderModule):
    def __init__(self, schema_type=None, *args, **kwargs):
        if schema_type is None:
            schema_type = FitTransformsByPointMatchParameters
        super(FitTransformsByPointMatch, self).__init__(
            schema_type=schema_type, *args, **kwargs)

    def run(self):
        if self.args['transform_type'] == 'rigid':
            Transform=RigidModel
        else:
            logger.debug('CHOOSING AFFINE MODEL')
            Transform=AffineModel

        tilespecs=fit_transforms_by_pointmatch(self.render,
                                     self.args['src_stack'],
                                     self.args['dst_stack'],
                                     self.args['matchcollection'],
                                     self.args['num_local_transforms'],
                                     Transform)

        outstack = self.args['output_stack']

        self.render.run(renderapi.stack.delete_stack, outstack)
        self.render.run(renderapi.stack.create_stack, outstack)

        renderapi.client.import_tilespecs_parallel(outstack,tilespecs,
                                                    render=self.render,
                                                    close_stack=True)
        
        self.render.run(renderapi.stack.set_stack_state,
                        outstack, state='COMPLETE')
    


if __name__ == "__main__":
    mod = FitTransformsByPointMatch(input_data=example_json)
    mod.run()
