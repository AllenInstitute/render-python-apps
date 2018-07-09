import renderapi
from ..module.render_module import RenderModule, RenderParameters
from argschema.fields import Str, Int, List

example_json = {
    "render": {
        "host": "ibs-forrestc-ux1",
        "port": 8080,
        "owner": "6_ribbon_experiments",
        "project": "M335503_Ai139_smallvol",
        "client_scripts" : "/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    "stack": "Rough_Aligned_Deconv_1_PSD95",
    "state": "COMPLETE"
}

class SetStackStateParameters(RenderParameters):
    stack = Str(required=False,default="",
                description= 'stack to change state of')
    state = Str(required=True, description = "State to set: LOADING or COMPLETE")

class SetStackState(RenderModule):
    def __init__(self, schema_type=None, *args, **kwargs):
        if schema_type is None:
            schema_type = SetStackStateParameters
        super(SetStackState, self).__init__(
            schema_type=schema_type, *args, **kwargs)

    def run(self):

	if self.args['stack'] == "":
	    allstacks = renderapi.render.get_stacks_by_owner_project(render=self.render)
	else:
	    allstacks = [self.args['stack'] ]
        for stack in allstacks:
            renderapi.stack.set_stack_state(stack, self.args['state'],
                render=self.render)
        
if __name__ == "__main__":
    mod = SetStackState(input_data=example_json)
    mod.run()
