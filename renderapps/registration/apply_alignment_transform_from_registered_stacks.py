import marshmallow as mm
from .apply_alignment_transform_from_registered_stack import ApplyAlignmentFromRegisteredStackParametersBase,ApplyAlignmentFromRegisteredStack,ApplyAlignmentFromRegisteredStackParameters

from renderapps.module.render_module import RenderModule


example_json = {
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":8080,
        "owner":"S3_Run1",
        "project":"S3_Run1_Jarvis",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    "prealigned_stack":"Rough_Aligned_68_to_112_DAPI_1_fullscale_CONS",
    "postaligned_stack":"Fine_Aligned_68_to_112_DAPI_1_188to694_fullscale_R1_R3",
    "registered_stacks":["Rough_Aligned_68_to_112_GFP_fullscale_CONS"],
    "old_prefix":"Rough_Aligned_",
    "new_prefix":"Fine_Aligned_R1_R3_",
    "stackResolutionX":1,
    "stackResolutionY":1,
    "stackResolutionZ":1,
    "pool_size":20
}

class ApplyAlignmentFromRegisteredStacksParameters(ApplyAlignmentFromRegisteredStackParametersBase):
    registered_stacks = mm.fields.List(mm.fields.Str,required=True,
        metadata={'description':'list of source_stacks that are registered with prealignedstack,\
                   but which you want to re-express in the space of postalignedstack'})           

    old_prefix = mm.fields.Str(required=False,default = None,
        metadata={'description':'old prefix to strip off of stack names'})

    new_prefix = mm.fields.Str(required=False,default = None,
        metadata={'description':'new prefix to add to stack names for output stacks'})


class ApplyAlignmentFromRegisteredStacks(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = ApplyAlignmentFromRegisteredStacksParameters
        super(ApplyAlignmentFromRegisteredStacks,self).__init__(schema_type=schema_type,*args,**kwargs)

    def run(self):
        self.logger.error('WARNING NEEDS TO BE TESTED, TALK TO FORREST IF BROKEN')

        oldprefix = self.args.get('old_prefix',None)
        newprefix = self.args.get('new_prefix',None)

        #loop over the target stacks
        for sourcestack in self.args['registered_stacks']:
            if oldprefix is not None:
                outstack = sourcestack.replace(oldprefix, '')
            if newprefix is not None:
                outstack = newprefix + outstack

            params = dict(self.args)
            del params['registered_stacks']
            del params['old_prefix']
            del params['new_prefix']
            params['source_stack']=sourcestack
            params['output_stack']=outstack
            #run the submodule not parsing command line arguments
            submod = ApplyAlignmentFromRegisteredStack(input_data = params,args=[])
            submod.run()

 
if __name__ == "__main__":
    mod = ApplyAlignmentFromRegisteredStacks(input_data= example_json)
    mod.run()

