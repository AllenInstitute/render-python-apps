#!/usr/bin/env python
import renderapi
from renderapi.transform import AffineModel, ReferenceTransform
from ..module.render_module import RenderModule, RenderParameters
from functools import partial
import tempfile
import os
import numpy as np
from argschema.fields import Str, Float, Int
import json

#An example set of parameters for this module
example_parameters = {
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":80,
        "owner":"Forrest",
        "project":"M246930_Scnn1a_4_f1",
        "client_scripts":"/pipeline/allenrender/render-ws-java-client/src/main/scripts"
    },
    "input_stack":"ROT_FA_STI_DCV_FF_Session1",
    "output_stack":"BIG_ROT_FA_STI_DCV_FF_Session1",
    "transformId":"rotate_and_enlarge",
    "M00":0,
    "M10":33.333,
    "M01":-33.333,
    "M11":0,
    "B0": 304867,  
    "B1": 8776,
    "pool_size":2
}

class ApplyAffineParametersBase(RenderParameters):
    transformId = Str(required=True,description='transform reference name to use when applying changes')
    M00 = Float(required=False,default=1.0,description='M00 (x\'=M00*x element of affine (default 1.0)')
    M10 = Float(required=False,default=0.0,description='M10 (y\'=M10*x element of affine (default 0.0)')
    M01 = Float(required=False,default=0.0,description='M01 (x\'=M01*y element of affine (default 0.0)')
    M11 = Float(required=False,default=1.0,description='M11 (y\'=M11*y) element of affine (default 1.0)')
    B0 = Float(required=False,default=0.0,description='B0 (x translation) element of affine (defautl 0.0)')
    B1 = Float(required=False,default=0.0,description='B1 (y translation) element of affine (default 0.0)')
    zmin = Int(required=False,description='zvalue to start')
    zmax = Int(required=False,description='zvalue to end')
    pool_size = Int(required=False,default=20,description='size of pool for parallel processing (default=20)')
class ApplyAffineParameters(ApplyAffineParametersBase):
    input_stack = Str(required=True,description='stack to apply affine to')
    output_stack = Str(required=False,description='stack to save answer into (defaults to overwriting input_stack)')


#define a function to process one z value
def process_z(render,input_stack,tform,z):
    
    changes_list =[]
    #get the tilespecs for this Z
    tilespecs = render.run( renderapi.tilespec.get_tile_specs_from_z,
                            input_stack,
                            z)
    #loop over the tilespes adding the transform
    for ts in tilespecs:
        d={'tileId':ts.tileId,
          'transform':tform.to_dict()}
        changes_list.append(d)
       
    #open a temporary file
    #tid,tfile = tempfile.mkstemp(suffix='.json')
    #file = open(tfile,'w')
    #write the file to disk
    #json.dump(changes_list,file)
    #os.close(tid)
    #return the filepath
    return changes_list

class ApplyAffine(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = ApplyAffineParameters
        super(ApplyAffine,self).__init__(schema_type=schema_type,*args,**kwargs)

    def run(self):
        #get the z values in the stack
        zvalues = self.render.run(renderapi.stack.get_z_values_for_stack,self.args['input_stack'])
        zvalues = np.array(zvalues)
        print(zvalues)
        zmin = self.args.get('zmin',np.min(zvalues))
        zmax = self.args.get('zmax',np.max(zvalues))
        zvalues = zvalues[zvalues>=zmin]
        zvalues = zvalues[zvalues<=zmax]



        #output_stack defaults to input_stack
        input_stack = self.args['input_stack']
        output_stack = self.args.get('output_stack',input_stack)

        tformid = '{}_to_{}'.format(input_stack,output_stack)

        #define the affine transform to apply everywhere
        global_tform = AffineModel(M00=self.args['M00'],
                            M10=self.args['M10'],
                            M01=self.args['M01'],
                            M11=self.args['M11'],
                            B0=self.args['B0'],
                            B1=self.args['B1'])
        #global_tform_ref = ReferenceTransform(refId=tformid)
        
        
        if (self.args['input_stack'] != output_stack):
            self.render.run(renderapi.stack.create_stack,output_stack)
        print "made stack"
        ds =",".join(global_tform.dataString.split(" "))
        renderapi.client.transformSectionClient(input_stack,
                                                self.args['transformId'],
                                                global_tform.className,
                                                ds,
                                                list(zvalues),
                                                targetStack=output_stack,
                                                replaceLast = False,
                                                render=self.render)
        sv = renderapi.stack.get_stack_metadata(input_stack, render=self.render)
        renderapi.stack.set_stack_metadata(output_stack,sv, render=self.render)
        renderapi.stack.set_stack_state(output_stack,'COMPLETE', render=self.render)
        #clean up the temp files
        #os.remove(tfile)
        #print json.dumps(tforms,indent=2)
        #print tfile
if __name__ == "__main__":
    mod = ApplyAffine(input_data= example_parameters)
    mod.run()
