import renderapi
import os
from pathos.multiprocessing import Pool
from functools import partial
from renderapps.module.render_module import RenderModule, RenderParameters
from json_module import InputFile, InputDir
import marshmallow as mm

example_json={
        "render":{
            "host":"ibs-forrestc-ux1",
            "port":8080,
            "owner":"Forrest",
            "project":"M247514_Rorb_1",
            "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
        },
        "example":"my example parameters",
}

class TemplateParameters(RenderParameters):
    example = mm.fields.Str(required=True,
        metadata={'description':'an example'})
    default_val = mm.fields.Str(required=False,default="a default value",
        metadata={'description':'an example with a default'})


class Template(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = TemplateParameters
        super(Template,self).__init__(schema_type=schema_type,*args,**kwargs)
    def run(self):
        print mod.args

if __name__ == "__main__":
    mod = Template(input_data= example_json)
    mod.run()
