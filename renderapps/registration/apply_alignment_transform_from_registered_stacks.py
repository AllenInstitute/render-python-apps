
from renderapps.registration.apply_alignment_transfrom_form_registered_stack import ApplyAlignmentFromRegisteredStackParametersBase,ApplyAlignmentFromRegisteredStack
from renderapps.module.RenderModule import RenderModule
import marshmallow as mm

example_json = {
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":8080,
        "owner":"Forrest",
        "project":"M247514_Rorb_1",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    "prealigned_stack":"REG_MARCH_21_DAPI_1",
    "postaligned_stack":"ALIGN2_MARCH_24b_DAPI_1",
    "registered_stacks":["REG_MARCH_21_MBP_deconvnew",
                         "REG_MARCH_21_GABA_deconvnew",
                         "REG_MARCH_21_GAD2_deconvnew",
                         "REG_MARCH_21_GluN1_deconvnew",
                         "REG_MARCH_21_PSD95_deconvnew",
                         "REG_MARCH_21_TdTomato_deconvnew",
                         "REG_MARCH_21_VGlut1_deconvnew",
                         "REG_MARCH_21_synapsin_deconvnew",
                         "REG_MARCH_21_DAPI_1_deconvnew",
                         "REG_MARCH_21_Gephyrin_deconvnew"],
    "old_prefix":"REG_MARCH_21_",
    "new_prefix":"ALIGN2_MARCH24b_",
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
            mod = ApplyAlignmentFromRegisteredStack(input_data = params,args=[])
            mod.run()

 
if __name__ == "__main__":
    mod = ApplyAlignmentFromRegisteredStacks(input_data= example_json)
    mod.run()

