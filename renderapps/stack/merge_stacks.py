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
    "stacks": ["BIGALIGN_LENS_EMclahe_Site3",
            "BIGALIGN_LENS_EMclahe_Site4",
            "BIGALIGN_LENS_EMclahe_Take2Site3",
            "BIGALIGN_LENS_EMclahe_Take2Site4",
            "BIGALIGN_LENS_EMclahe_Take2Site5"],
    "output_stack": "BIGALIGN_LENS_EMclahe_all"
}

class MergeStacksParameters(RenderParameters):
    stacks = List(Str,required=True,
                description= 'stacks to merge tiles from')
    output_stack = Str(required=False, 
                           description= 'stack to save tiles into')


class MergeStacks(RenderModule):
    def __init__(self, schema_type=None, *args, **kwargs):
        if schema_type is None:
            schema_type = MergeStacksParameters
        super(MergeStacks, self).__init__(
            schema_type=schema_type, *args, **kwargs)

    def run(self):
        outstack = self.args['output_stack']
        renderapi.stack.create_stack(outstack,render=self.render)

        for stack in self.args['stacks']:
            tilespecs = renderapi.tilespec.get_tile_specs_from_stack(stack, render=self.render)
            renderapi.client.import_tilespecs_parallel(outstack,tilespecs,render=self.render,close_stack=False)

            stack_metadata = renderapi.stack.get_stack_metadata(
                    stack, render=self.render)

        renderapi.stack.set_stack_metadata(outstack,stack_metadata,render=self.render)
        renderapi.stack.set_stack_state(outstack,"COMPLETE",render=self.render)

if __name__ == "__main__":
    mod = MergeStacks(input_data=example_json)
    mod.run()
