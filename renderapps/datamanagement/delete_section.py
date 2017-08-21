if __name__ == "__main__" and __package__ is None:
    __package__ = "renderapps.datamanagement.DeleteSection"
import json
import os
import renderapi
from ..module.render_module import RenderModule,RenderParameters
from json_module import InputFile,InputDir,OutputDir
import marshmallow as mm
from functools import partial
import glob
import time
import numpy as np

#Author: Sharmishtaa Seshamani

example_parameters={
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":80,
        "owner":"SC_MT_IUE1_2",
        "project":"SC_MT22_IUE1_2_PlungeLowicryl",
        "client_scripts":"/var/www/render/render-ws-java-client/src/main/scripts"
    },
    'input_stack':'Registered_DAPI2',
    'section_z': 301
}

class DeleteSectionParameters(RenderParameters):
    input_stack = mm.fields.Str(required=True,
        metadata={'description':'Input Stack'})
    section_z = mm.fields.Int(required=True,
        metadata={'description':'Section to Delete'})


class DeleteSection(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = DeleteSectionParameters
        super(DeleteSection,self).__init__(schema_type=schema_type,*args,**kwargs)
    def run(self):

		allzvalues = self.render.run(renderapi.stack.get_z_values_for_stack,self.args['input_stack'])
		print "Number of z values:"
		a = np.array(allzvalues)
		print a
		print self.args['input_stack']
		print self.args['section_z']
		
		renderapi.stack.set_stack_state(self.args['input_stack'], state='LOADING', render=self.render)
		
		renderapi.stack.delete_section(self.args['input_stack'],int(self.args['section_z']),render=self.render)
		
		renderapi.stack.set_stack_state(self.args['input_stack'], state='COMPLETE', render=self.render)
		
		#renderapi.stack.create_stack(self.args['output_stack'],cycleNumber=5,cycleStepNumber=1, render=self.render)
        #renderapi.client.import_jsonfiles_parallel(self.args['output_stack'],jsonfiles,render=self.render)



if __name__ == "__main__":
    #mod = DeleteSection(input_data=example_parameters)
    mod = DeleteSection(schema_type = DeleteSectionParameters)
    mod.run()
