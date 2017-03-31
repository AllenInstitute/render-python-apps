#!/usr/bin/env python
import renderapi
from renderapps.module.render_module import RenderModule,RenderParameters
import marshmallow as mm

#An example set of parameters for this module
example_parameters = {
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":8080,
        "owner":"Forrest",
        "project":"M247514_Rorb_1",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    'input_stack':'ALIGNEM_reg2',
    'output_stack':'ALIGNEM_reg2_clahe'
}
class CopyMetaDataParameters(RenderParameters):
    input_stack = mm.fields.Str(required=True,metadata={'description':'stack to copy from'})
    output_stack = mm.fields.Str(required=True,metadata={'description':'stack to copy to'})

class CopyMetaDataModule(RenderModule):
    def __init__(self,*args,**kwargs):
        super(CopyMetaDataModule,self).__init__(*args,**kwargs)

    def run(self):
        sv = self.render.run(renderapi.stack.get_stack_metadata,self.args['input_stack'])
        self.render.run(renderapi.stack.set_stack_metadata,self.args['output_stack'],sv)
        self.render.run(renderapi.stack.set_stack_state,self.args['output_stack'],'COMPLETE')


if __name__ == '__main__':
    #process the command line arguments
    mod = CopyMetaDataModule(schema_type=CopyMetaDataParameters,input_data=example_parameters)
    mod.run()
