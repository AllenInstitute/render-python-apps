import os
import renderapi
from pathos.multiprocessing import Pool
from render_module import RenderModule,RenderParameters
from json_module import InputFile,InputDir
import marshmallow as mm

class TemplateParameters(RenderParameters):
    example = mm.fields.Str(required=True,default=None,
        metadata={'description':'an example'})


class Template(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = TemplateParameters
        super(Template,self).__init__(schema_type=schema_type,*args,**kwargs)
    def run(self):
        print mod.args

if __name__ == "__main__":
    mod = Template()
    mod.run()
