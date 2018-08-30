from renderapps.module.render_module import RenderParameters, RenderModule
import argschema
from functools import partial
import renderapi
import os


example_parameters = {
    "render":{
        "host": "ibs-forrestc-ux1",
        "port": 80,
        "owner": "multchan",
        "project": "M335503_Ai139_smallvol",
        "client_scripts": "/pipeline/allenrender/render-ws-java-client/src/main/scripts"
    },
    "base_stack":"ACQ_Session1",
    "session_stacks":[
        {"stack":"ACQ_Session1",
        "channel_suffix": "_raw"},
        {"stack":"FF_Session1",
        "channel_suffix": "_ff"}#,
        # {"stack":"DCV_Session1",
        # "channel_suffix": "_dcv"}
    ],
    "output_stack":"TESTALL_Session1"
}

class SessionStackParameters(argschema.schemas.DefaultSchema):
    stack = argschema.fields.Str(required=True,
                                 description="stack to merge")
    channel_suffix = argschema.fields.Str(required=True,
                    description = "what to append to channel names from this stack")

class MergeSessionStacksParameters(RenderParameters):
    base_stack = argschema.fields.Str(required=True,description="stack to base tilespecs from")
    session_stacks = argschema.fields.Nested(SessionStackParameters, many=True,required=True, description="channelname:stack dictionary to find mipmap levels by frame")
    output_stack = argschema.fields.Str(required=True,description="output stack to save tilespecs in")
    
#define a standard function for making a json file from render
#returning the filepath to that json, and a list of the framenumbers
def get_tilespecs_and_framenumbers(render,stack,z):
    tilespecs = render.run(renderapi.tilespec.get_tile_specs_from_z,stack,z)
    def get_framenumber(filepath):
        return int(os.path.split(filepath)[1].split('_F')[-1][0:4])
    framenumbers = [get_framenumber(ts.ip.get(0)['imageUrl']) for ts in tilespecs]
    return tilespecs,framenumbers

def process_z(render,base_stack, session_stacks,output_stack,z):
    #use the function to make jsons for aligned and input stacks
    # for session_stack in session_stacks:
    #     true_base = next(name for name,stack in session_stack)
    base_tilespecs,base_framenumbers = get_tilespecs_and_framenumbers(render, base_stack, z)
    for bts in base_tilespecs:
        bts.channels = []

    for stack in session_stacks:
        sess_stack_tilespecs,sess_framenumbers = get_tilespecs_and_framenumbers(render, stack['stack'], z)
        for bts,bfn in zip(base_tilespecs,base_framenumbers):
            cts = next(t for t,fn in zip(sess_stack_tilespecs,sess_framenumbers) if fn==bfn)
            chans = cts.channels
            for c in chans:
                c.name = c.name + stack['channel_suffix']
            if bts.channels is None:
                bts.channels = []
            bts.channels = bts.channels+cts.channels
     
  
    renderapi.client.import_tilespecs(output_stack,base_tilespecs,render=render)
    
class MergeSessionStacks(RenderModule):
    default_schema = MergeSessionStacksParameters

    def run(self):
        zvalues = renderapi.stack.get_z_values_for_stack(mod.args['base_stack'],render=self.render)
        my_partial = partial(process_z,
                             self.render,
                             self.args['base_stack'],
			                 self.args['session_stacks'],
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
