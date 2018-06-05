import argschema
import renderapi
from renderapps.TrakEM2.trakem2utils import get_matching_tilespec_by_path
from renderapps.module.render_module import TrakEM2RenderModule,RenderTrakEM2Parameters
import logging

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
                render=self.render)

        #replace the old tileIds with the ones in input_stack
        for ts in tem2_tilespecs:
            ts_render = get_matching_tilespec_by_path(ts,render_tilespecs)
            ts.tileId = ts_render.tileId
            mml = renderapi.tilespec.MipMapLevel(0,ts_render.ip.get(0)['imageUrl'],ts_render.ip.get(0)['maskUrl'])
            ts.channels=[]
            ts.ip.update(mml)

        renderapi.stack.logger.setLevel(logging.DEBUG)
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
        "input_stack":"Site3Align_EM",
        "output_stack":"Site3Align2_EM",
        "tem2project": "/nas/data/M247514_Rorb_1/EMraw/ribbon0000/Site3Aligned.xml",
        "renderHome": "/pipeline/render"
    }
    mod = CreateRenderStackFromTrakEM2(input_data = example_input)
    mod.run()

