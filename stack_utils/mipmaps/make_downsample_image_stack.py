import json
import os
import renderapi
from pathos.multiprocessing import Pool
from render_module import RenderModule,RenderParameters
from json_module import InputFile,InputDir,OutputDir
import marshmallow as mm
from functools import partial


example_parameters=
{
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":80,
        "owner":"Sharmishtaas",
        "project":"M247514_Rorb_1",
        "client_scripts":"/var/www/render/render-ws-java-client/src/main/scripts"
    },
    'input_stack':'REG_MARCH_21_DAPI_1',
    'output_stack':'REG_MARCH_21_DAPI_1_sections',
    'image_directory':'/nas3/data/M247514_Rorb_1/processed/downsampled_sections',
    'pool_size':5
}

class MakeDownsampleSectionStackParameters(RenderParameters):
    input_stack = mm.fields.Str(required=True,)
        metadata={'description':'stack to make a downsample version of'})
    scale = mm.fields.Float(required=False,default = .01,
        metadata={'description':'scale to make images'})
    image_directory = OutputDir(required=True,
        metadata={'decription','path to save section images'})
    output_stack = mm.fields.Str(required=True,
        metadata={'description':'output stack to name'})
    pool_size = mm.fields.Int(require=False,default=20,
        metadata={'description':'number of parallel threads to use'})

#       @Parameter(names = "--stack", description = "Stack name", required = true)
# private String stack;
#
# @Parameter(names = "--rootDirectory", description = "Root directory for rendered layers (e.g. /tier2/flyTEM/nobackup/rendered_boxes)", required = true)
# private String rootDirectory;
#
# @Parameter(names = "--scale", description = "Scale for each rendered layer", required = false)
# private Double scale = 0.02;
#
# @Parameter(names = "--format", description = "Format for rendered boxes", required = false)
# private String format = Utils.PNG_FORMAT;
#
# @Parameter(names = "--doFilter", description = "Use ad hoc filter to support alignment", required = false, arity = 1)
# private boolean doFilter = true;
#
# @Parameter(names = "--fillWithNoise", description = "Fill image with noise before rendering to improve point match derivation", required = false, arity = 1)
# private boolean fillWithNoise = true;
#
# @Parameter(description = "Z values for sections to render", required = true)
# private List<Double> zValues;
#


def process_z(render,stack,output_dir,scale,z):
    args=['--stack', stack,
          '--rootDirectory',output_dir ,
          '--scale',str(scale),
          str(z)]
    self.render.run(renderapi.client.call_run_ws_client,
        'org.janelia.render.client.RenderSectionClient',
        add_args = args)

class MakeDownsampleSectionStack(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = MakeDownsampleSectionStackParameters
        super(CreateFastStack,self).__init__(schema_type=schema_type,*args,**kwargs)
    def run(self):
        zvalues = self.render.run(renderapi.stack.get_z_values_for_stack,
            self.args['input_stack'])

        pool = Pool(self.args['pool_size'])
        mypartial = partial(process_z,self.args['input_stack'],
            self.args['output_dir'],self.args['scale'])
        pool.map(mypartial,zvalues)



if __name__ == "__main__":
    mod = MakeDownsampleSectionStack(input_data=example_parameters)
    mod.run()
