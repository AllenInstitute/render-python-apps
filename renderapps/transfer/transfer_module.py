from ..module.render_module import RenderClientParameters
from json_module import InputFile, InputDir
from json_module import JsonModule,ModuleParameters
import marshmallow as mm
import renderapi

class RenderTransferParameters(ModuleParameters):
    render_source = mm.fields.Nested(RenderClientParameters)
    render_target = mm.fields.Nested(RenderClientParameters)

class RenderTransfer(JsonModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = RenderTransferParameters
        super(RenderTransfer,self).__init__(schema_type = schema_type,*args,**kwargs)
        self.render_source = renderapi.render.connect(**self.args['render_source'])
        self.render_target = renderapi.render.connect(**self.args['render_target']) 
