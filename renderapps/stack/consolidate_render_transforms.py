import numpy as np
from renderapi.transform import AffineModel,Polynomial2DTransform
from functools import partial
import os
import renderapi
from ..module.render_module import RenderModule, RenderParameters
from argschema.fields import InputFile, InputDir, Str, Int

example_json={
    "render":{
        "host":"http://ibs-forrestc-ux1",
        "port":80,
        "owner":"Forrest",
        "project":"M247514_Rorb_1",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    "stack":"ROUGHALIGN_LENS_DAPI_1_deconvnew",
    "pool_size":20
}
class ConsolidateTransformsParameters(RenderParameters):
    stack = Str(required=True,
        description='stack to consolidate')
    postfix = Str(required=False, default="_CONS",
        description='postfix to add to stack name on saving if no output defined (default _CONS)')
    output_stack = Str(required=False,
        description='name of output stack (default to adding postfix to input)')
    pool_size = Int(required=False, default=20,
        description='name of output stack (default to adding postfix to input)')

def consolidate_transforms(tforms, logger, makePolyDegree=0):
    tform_total = AffineModel()
    start_index = 0
    total_affines = 0
    new_tform_list = []

    for i,tform in enumerate(tforms):
        if 'AffineModel2D' in tform.className:
            total_affines+=1
            tform_total = tform.concatenate(tform_total)
            #tform_total.M=tform.M.dot(tform_total.M)
        else:
            logger.debug('consolidate_transforms: non affine {}'.format(tform))
            if total_affines>0:
                if makePolyDegree>0:
                    polyTform = Polynomial2DTransform().fromAffine(tform_total)
                    polyTform=polyTform.asorder(makePolyDegree)
                    new_tform_list.append(polyTform)
                else:
                    new_tform_list.append(tform_total)
                tform_total = AffineModel()
                total_affines =0
            new_tform_list.append(tform)
    if total_affines>0:
        if makePolyDegree>0:
            polyTform = Polynomial2DTransform().fromAffine(tform_total)
            polyTform=polyTform.asorder(makePolyDegree)
            new_tform_list.append(polyTform)
        else:
            new_tform_list.append(tform_total)
    return new_tform_list

def process_z_make_json(r, stack, outstack, logger, json_dir, z):
    tilespecs = r.run(renderapi.tilespec.get_tile_specs_from_z, stack, z)

    for ts in tilespecs:
        logger.debug('process_z_make_json: tileId {}'.format(ts.tileId))
        ts.tforms = consolidate_transforms(ts.tforms, logger)
        logger.debug('consolatedate tformlist {}'.format(ts.tforms[0]))

    logger.debug("tileid:{} transforms:{}".format(tilespecs[0].tileId,tilespecs[0].tforms))
    json_filepath = os.path.join(json_dir, '%s_%04d'%(outstack,z))
    renderapi.utils.renderdump(tilespecs, open(json_filepath, 'w'), indent=4)
    return tilespecs

class ConsolidateTransforms(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = ConsolidateTransformsParameters
        super(ConsolidateTransforms,self).__init__(schema_type=schema_type, *args, **kwargs)
    def run(self):
        stack = self.args['stack']
        outstack= self.args.get('output_stack',None)
        if outstack is None:
            outstack=stack+ self.args['postfix']

        json_dir = '/nas3/data/%s/processed/consolidated_affine_json/'%(self.args['render']['project'])
        if not os.path.isdir(json_dir):
            os.makedirs(json_dir)


        zvalues=self.render.run(renderapi.stack.get_z_values_for_stack, stack)
        with renderapi.client.WithPool(self.args['pool_size']) as pool:
            json_files=pool.map(partial(process_z_make_json, self.render, stack, outstack, self.logger, json_dir), zvalues)

        self.render.run(renderapi.stack.delete_stack,outstack)
        self.render.run(renderapi.stack.create_stack,outstack)
        self.render.run(renderapi.client.import_jsonfiles_parallel, outstack, json_files)


if __name__ == "__main__":
    mod = ConsolidateTransforms(input_data=example_json)
    mod.run()
