import renderapi
import os
from ..module.render_module import RenderModule, RenderParameters
import argschema
import numpy as np

example_json={
        "render":{
            'host':'ibs-forrestc-ux1',
            'port':8080,
            'owner':'Forrest',
            'project':'M247514_Rorb_1',
            'client_scripts':'/var/www/render/render-ws-java-client/src/main/scripts'
        },
        "stack":"BIGALIGN_LENS_DAPI_1_deconvnew",
        "roi":[[165000,-126000],[176000,-126000],[176000,-115000],[165000,-115000]],
        "zrange":[0,50],
        "xml_file":"test_out.xml"
}

class CreateFibicsXMLParameters(RenderParameters):
    stack = argschema.fields.Str(required=True,
        description='render stack to get roi from')
    xml_file = argschema.fields.OutputFile(required=True,
        description='path to same fibics xml file')
    roi = argschema.fields.NumpyArray(dtype=np.float,
        description='Nx2 (x,y) array of roi points, not closed')
    zrange = argschema.fields.List(argschema.fields.Int,required=True,
        description='range of z values to include in output min,max')

class CreateFibicsXML(RenderModule):
    default_schema = CreateFibicsXMLParameters
    
    def run(self):
        print self.args['zrange']
        self.logger.error('WARNING NEEDS TO BE TESTED, TALK TO FORREST IF BROKEN')


if __name__ == "__main__":
    mod = CreateFibicsXML(input_data= example_json)
    mod.run()
