import os
import renderapi
from functools import partial
from ..module.render_module import RenderModule,RenderParameters
from ..module.json_module import InputFile,InputDir
import marshmallow as mm
import tempfile
example_json = {
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":8080,
        "owner":"Forrest",
        "project":"M247514_Rorb_1",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    "stack":"BIGALIGN2_MARCH24c_DAPI_1_deconvnew",
    "minIntensity":0,
    "maxIntensity":2000,
    "pool_size":20
}

class SetStackLevelsParameters(RenderParameters):
    stack = mm.fields.Str(required=True,
        metadata={'description':'name of stack to edit'})
    minIntensity = mm.fields.Int(required=False,default=None,
        metadata={'description':'minIntensity to set for stack (default: do not change)'})
    maxIntensity = mm.fields.Int(required=False,default=None,
                metadata={'description':'maxIntensity to set for stack (default: do not change)'})
    pool_size = mm.fields.Int(required=False,default=20,
        metadata={'description':'degree of parallelism to use (default to 20)'})

#define a function for a single z value
def process_z(render,stack,minIntensity,maxIntensity, z):
    tilespecs = render.run(renderapi.tilespec.get_tile_specs_from_z,stack,z)
    #loop over all input tilespecs
    for ts in tilespecs:
        if minIntensity is not None:
            ts.minint = minIntensity
        if maxIntensity is not None:
            ts.maxint = maxIntensity
    output_json_filepath = tempfile.mktemp(suffix='.json')
    with open(output_json_filepath,'w') as fp:
        renderapi.utils.renderdump(tilespecs,fp)
        fp.close()
    return output_json_filepath

class SetStackLevels(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = SetStackLevelsParameters
        super(SetStackLevels,self).__init__(schema_type=schema_type,*args,**kwargs)
    def run(self):
        zvalues=self.render.run(renderapi.stack.get_z_values_for_stack,self.args['stack'])
        self.logger.info('SetStackLevels: making json files for stack %s'%self.args['stack'])
        self.logger.debug('SetStackLevels: with min{} max {}'.format(self.args['minIntensity'],self.args['maxIntensity']))

        mypartial = partial(process_z,self.render,self.args['stack'],self.args['minIntensity'],self.args['maxIntensity'])
        with renderapi.client.WithPool(self.args['pool_size']) as pool:
            jsonFilePaths = pool.map(mypartial,zvalues)
        self.logger.info('SetStackLevels: uploading json files for stack %s'%self.args['stack'])
        self.logger.debug('SetStackLevels: temp files {}'.format(jsonFilePaths))
        self.render.run(renderapi.client.import_jsonfiles_parallel,self.args['stack'], jsonFilePaths, poolsize=self.args['pool_size'])
        self.render.run(renderapi.stack.set_stack_state,self.args['stack'],state='COMPLETE')

if __name__ == "__main__":
    mod = SetStackLevels(input_data = example_json)
    mod.run()
