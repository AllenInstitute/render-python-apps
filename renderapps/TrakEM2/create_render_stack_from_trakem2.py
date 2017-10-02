import argschema
import renderapi
from .trakem2utils import get_matching_tilespec_by_path
from ..module.render_module import TrakEM2RenderModule,RenderTrakEM2Parameters

class CreateRenderStackFromTrakEM2Parameters(RenderTrakEM2Parameters):
    input_stack = argschema.fields.Str(required=True,
        description="name of render stack to get tileIds from")
    output_stack = argschema.fields.Str(required=True,
        description="name of render stack to save into")
    tem2project = argschema.fields.InputFile(required=True,
        description="path to trakem2 project")

class CreateRenderStackFromTrakEM2(TrakEM2RenderModule):
    default_schema=CreateRenderStackFromTrakEM2Parameters

    def run(self):
        #convert the project to tilespecs
        tem2_tilespecs=self.get_trakem2_tilespecs(self.args['tem2project'])

        #get input_stack tilespecs
        render_tilespecs = renderapi.tilespec.get_tile_specs_from_stack(
                self.args['input_stack'],
                self.render)

        #replace the old tileIds with the ones in input_stack
        for ts in tem2_tilespecs:
            ts_render = get_matching_tilespec_by_path(ts,render_tilespecs)
            ts.tileId = ts_render.tileId

        #create a new stack
        renderapi.stack.create_stack(self.args['output_stack'],
                                     render=self.render)

        #upload these tilespecs to it
        renderapi.client.import_tilespecs_parallel(self.args['output_stack'],
                                                   tem2_tilespecs,
                                                   render=self.render)
                    
if __name__ == '__main__':
    example_input = {
        "render": {
            "host": "ibs-forrestc-ux1",
            "port": 8080,
            "owner": "Forrest",
            "project": "M247514_Rorb_1",
            "client_scripts": "/pipeline/render/render-ws-java-client/src/main/scripts"
        },
        "input_stack":"ALIGNEM_reg2",
        "output_stack":"",
        "tem2project": "/nas4/data/EM_annotation/annotationFilesForJHU/annotationTrakEMprojects_M247514_Rorb_1/m247514_Site3Annotation_RD.xml",
        "renderHome": "/pipeline/render"
    }
    mod = CreateRenderStackFromTrakEM2(input_data = example_input, args=[])
    mod.run()

