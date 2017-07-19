from ..module.render_module import RenderClientParameters
import argschema
import renderapi


class RenderTransferParameters(argschema.schemas.ArgSchema):
    render_source = argschema.fields.Nested(RenderClientParameters)
    render_target = argschema.fields.Nested(RenderClientParameters)

class RenderTransfer(argschema.ArgSchemaParser):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = RenderTransferParameters
        super(RenderTransfer,self).__init__(schema_type = schema_type,*args,**kwargs)
        self.render_source = renderapi.render.connect(**self.args['render_source'])
        self.render_target = renderapi.render.connect(**self.args['render_target'])
