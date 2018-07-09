from renderapps.module.render_module import RenderParameters, RenderModule
import argschema
from functools import partial
import renderapi
import os

example_parameters = {
    "render":{
        "host": "ibs-forrestc-ux1",
        "port": 80,
        "owner": "Forrest",
        "project": "M246930_Scnn1a_4_f1",
        "client_scripts": "/pipeline/allenrender/render-ws-java-client/src/main/scripts"
    },
    "base_stack":"Stitched_1_DAPI_1",
    "channel_stacks":{
        "DAPI1":"Deconvolved_1_DAPI_1",
        "DAPI1_FF":"Stitched_1_DAPI_1",
        "PSD95":"Deconvolved_1_PSD95",
        "GluN1_FF":"Flatfieldcorrected_1_PSD95",
        "VGlut1":"Deconvolved_1_VGlut1",
        "VGlut1_FF":"Flatfieldcorrected_1_VGlut1",
        "Gephyrin":"Deconvolved_1_Gephyrin",
        "Gephyrin_FF":"Flatfieldcorrected_1_Gephyrin",
    },
    "output_stack":"REG_STI_DCV_FF_Session1"
}

class MergeSessionStacksParameters(RenderParameters):
    base_stack = argschema.fields.Str(required=True,description="stack to base tilespecs from")
    channel_stacks = argschema.fields.Dict(required=True,description="channelname:stack dictionary to find mipmap levels by frame")
    output_stack = argschema.fields.Str(required=True,description="output stack to save tilespecs in")
    
#define a standard function for making a json file from render
#returning the filepath to that json, and a list of the framenumbers
def get_tilespecs_and_framenumbers(render,stack,z):
    tilespecs = render.run(renderapi.tilespec.get_tile_specs_from_z,stack,z)
    def get_framenumber(filepath):
        return int(os.path.split(filepath)[1].split('_F')[-1][0:4])
    framenumbers = [get_framenumber(ts.ip.get(0)['imageUrl']) for ts in tilespecs]
    return tilespecs,framenumbers

def process_z(render,base_stack, channel_stacks,output_stack,z):
    #use the function to make jsons for aligned and input stacks
    base_tilespecs,base_framenumbers = get_tilespecs_and_framenumbers(render, base_stack, z)
    
    for channelname,channelstack in channel_stacks.items():
        channel_tilespecs,channel_framenumbers = get_tilespecs_and_framenumbers(render, channelstack, z)
        for bts,bfn in zip(base_tilespecs,base_framenumbers):
            cts = next(t for t,fn in zip(channel_tilespecs,channel_framenumbers) if fn==bfn)
            channel = renderapi.channel.Channel(name=channelname,ip=cts.ip,maxIntensity=cts.maxint)
            if bts.channels is None:
                bts.channels = []
            if 'DAPI' in channelname:
                bts.channels = [channel]+bts.channels
            else:
                bts.channels.append(channel)
    renderapi.client.import_tilespecs(output_stack,base_tilespecs,render=render)
    
class MergeSessionStacks(RenderModule):
    default_schema = MergeSessionStacksParameters

    def run(self):
        zvalues = renderapi.stack.get_z_values_for_stack(mod.args['base_stack'],render=self.render)
        my_partial = partial(process_z,
                             self.render,
                             self.args['base_stack'],
                             self.args['channel_stacks'],
                             self.args['output_stack'])
        renderapi.stack.create_stack(self.args['output_stack'],render=self.render)
        with renderapi.client.WithPool(20) as pool:
            pool.map(my_partial,zvalues)
        #for z in zvalues:
        #    my_partial(z)
        #    break
        renderapi.stack.set_stack_state(self.args['output_stack'],'COMPLETE',render=self.render)
        
if __name__ == '__main__':
    mod=MergeSessionStacks(input_data=example_parameters,args=[])
    mod.run()