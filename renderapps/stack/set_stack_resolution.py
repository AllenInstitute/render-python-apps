import renderapi
from ..module.render_module import RenderModule, RenderParameters
from argschema.fields import Str, Int, List

example_json = {
    "render": {
        "host": "ibs-forrestc-ux1",
        "port": 8080,
        "owner": "Forrest",
        "project": "M247514_Rorb_1",
        "client_scripts" : "/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    "stacks": ["BIGALIGN_LENS_DAPI_1_deconvnew"],
    "stackResolutionX": 3,
    "stackResolutionY": 3,
    "stackResolutionZ": 50
}

class SetStackResolutionParameters(RenderParameters):
    stacks = List(Str,required=True,
                description= 'stack to change resolution of')
    stackResolutionX = Int(required=False, 
                           description= 'X stack resolution (nm)')
    stackResolutionY = Int(required=False, 
                           description= 'Y stack resolution (nm)')
    stackResolutionZ = Int(required=False, 
                           description= 'Z stack resolution (nm)')

class SetStackResolution(RenderModule):
    def __init__(self, schema_type=None, *args, **kwargs):
        if schema_type is None:
            schema_type = SetStackResolutionParameters
        super(SetStackResolution, self).__init__(
            schema_type=schema_type, *args, **kwargs)

    def run(self):
        for stack in self.args['stacks']:
        
            stackMetadata = renderapi.stack.get_stack_metadata(
                stack, render=self.render)
            
            stackMetadata.stackResolutionX = self.args.get(
                'stackResolutionX', stackMetadata.stackResolutionX)
            stackMetadata.stackResolutionY = self.args.get(
                'stackResolutionY', stackMetadata.stackResolutionY)
            stackMetadata.stackResolutionZ = self.args.get(
                'stackResolutionZ', stackMetadata.stackResolutionZ)
            
            stackMetadata = renderapi.stack.set_stack_metadata(
                stack, stackMetadata, render=self.render)
            
            renderapi.stack.set_stack_state(stack, 'COMPLETE',
                render=self.render)
        
if __name__ == "__main__":
    mod = SetStackResolution(input_data=example_json)
    mod.run()
