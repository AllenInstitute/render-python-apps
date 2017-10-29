if __name__ == "__main__" and __package__ is None:
    __package__ = "renderapps.heirarchical_alignment.split_stack"
import renderapi
from ..module.render_module import RenderModule, RenderParameters
from argschema.fields import InputFile, InputDir, Str, Float, Int, List
import numpy as np
import argschema
import json
example_input = {
    "render": {
        "host": "render-dev-eric.neurodata.io",
        "port": 8080,
        "owner": "flyTEM",
        "project": "trautmane_test",
        "client_scripts": "/Users/forrestcollman/RenderStack/render/render-ws-java-client/src/main/scripts"
    },
    "input_stack": "rough_tiles",
    "output_split_k":5,
    "output_size":1024,
    "pool_size": 5
}

# output_json = {
#     "output_stacks":["stack_1_0","stack_1_1","stack_1_2"],
#     "output_split_level":3,
#     "output_rows":1,
#     "output_columns"3
# }


# example_input = {
#     "render": {
#         "host": "ibs-forrestc-ux1",
#         "port": 8080,
#         "owner": "M246930_Scnn1a",
#         "project": "M246930_Scnn1a_4",
#         "client_scripts": "/var/www/render/render-ws-java-client/src/main/scripts"
#     },
#     "input_stacks": ['stack_1_0','stack_1_1','stack_1_2','stack_1_3','stack_5','stack_6','stack_7','stack_8','stack_9']
#     "output_split_level":5,
#     "pool_size": 20
# }

# output_json=
# {
#     "stacks_to_split":['stack_1','stack_2','stack_7'],
#     "stacks_to_copy":['stack_3','stack_4','stack_5','stack_6','stack_8','stack_9']
# }

class SplitStackParams(RenderParameters):
    input_stack = Str(required=True, description='Input stack')
    output_split_k = Int(required=True, description='Maximum number of rows/columns of split stack outputs')
    output_size = Int(required=True, description='approximate size of split tiles, one of height or width will be this')
    pool_size = Int(required=False,default=20,description='size of pool for parallel processing (default=20)')

class SplitStackOutputParams(argschema.schemas.DefaultSchema):
    output_stacks=List(Str,required=True, description = 'stacks this split into')
    rows = Int(required=True,description="number of rows this module split the input stack into")
    cols = Int(required=True, description="number of columns this modules split the input stack into")
    output_split_k = Int(required=True, description="output split level... repeated from input")
    
class SplitStack(RenderModule):
    default_schema=SplitStackParams

    def run(self):
        stack = self.args['input_stack']
        bounds = renderapi.stack.get_stack_bounds(stack,render=self.render)
        zvalues = renderapi.stack.get_z_values_for_stack(stack, render=self.render)
        width = bounds['maxX']-bounds['minX']
        height = bounds['maxY']-bounds['minY']
        max_dim = np.max([width,height])

        fov = max_dim/self.args['output_split_k']

        rows = int(np.round(height/fov))
        cols = int(np.round(width/fov))
        
        fov_height = height/rows
        fov_width = width/cols
        scale = self.args['output_size']/fov
        scale = np.min([1.0,scale])
        level = np.int(np.ceil(np.log2(1/scale)))
        level_scale = 1.0/np.power(2,level)
        print 'level',level
        print 'level_scale',level_scale
        
        
        #scale=1.0
        print 'scale',scale
        print 'fov_hw',fov_height,fov_width

        x = np.arange(bounds['minX'],bounds['maxX'],fov_width)
        y = np.arange(bounds['minY'],bounds['maxY'],fov_height)
        print x,y
        print len(x),len(y),cols,rows
        xx,yy =  np.meshgrid(x,y)
        fov_ds_width=int(np.round(fov_width)*scale)
        fov_ds_height=int(np.round(fov_height)*scale)

        fov_scale = 1.0*fov_width/fov_ds_width
        template = "http://{}:{}/render-ws/v1/owner/{}/project/{}/stack/{}/z/{}/box/{},{},{},{},{}/tiff-image?name=z{}.tif"
        render_args = self.args['render']

        for k,(xc,yc) in enumerate(zip(xx.ravel(),yy.ravel())):
            
                i,j=np.unravel_index(k,(rows,cols))
                #print i,k,xc,yc
                tform0 = renderapi.transform.AffineModel(M00=fov_scale,
                                                         M11=fov_scale,
                                                         labels=['scale'])
                tform1 = renderapi.transform.AffineModel(B0=-fov_width/2,
                                                         B1=fov_height/2,
                                                         labels=['middle_center'])
                tform2 = renderapi.transform.AffineModel(B0=xc+(fov_width/2),
                                                         B1=yc+(fov_height/2),
                                                         labels=['to_global'])
                tform3 = renderapi.transform.AffineModel(labels=['identity'])
                tforms = [tform0,tform1,tform2,tform3]

                outstack = stack + "_%d_v2"%k
                tilespecs = []
                #tform_id = 'boxtform_{}_{}_{}'.format( stack,i,j )
                #tform_list = renderapi.transform.TransformList([tform1,tform2,tform3], 
                #                                                transformId=)
                #ref_tform = renderapi

                for z in zvalues:
                    layout = renderapi.tilespec.Layout(sectionId="%2.1f"%z,
                                                       cameraId="virtual",
                                                       scopeId="heir_{}".format(self.args['output_split_k']),
                                                       imageRow=i,
                                                       imageCol=j,
                                                       rotation=0,
                                                       stageX=xc,
                                                       stageY=yc)
                    imageUrl = template.format(render_args['host'],
                                        render_args['port'],
                                        render_args['owner'],
                                        render_args['project'],
                                        stack,
                                        int(z),
                                        xc,
                                        yc,
                                        int(np.round(fov_width)),
                                        int(np.round(fov_height)),
                                        scale,
                                        int(z))
                    
                    mml = renderapi.tilespec.MipMapLevel(0,imageUrl=imageUrl)
                    tilespec= renderapi.tilespec.TileSpec(
                        tileId="{}_{}_{}_{}_{}".format(outstack,i,j,k,z),
                        mipMapLevels=[mml],
                        z=z,
                        tforms=tforms,
                        layout=layout,
                        maxint=255,
                        minint=0,
                        width = fov_ds_width,
                        height = fov_ds_height
                    )
                    
                    tilespecs.append(tilespec)
                
                #print json.dumps(tilespecs[0].to_dict(),indent=4)
                renderapi.stack.create_stack(outstack,render=self.render)
                #print renderapi.utils.renderdumps(tilespecs,indent=4)
                renderapi.client.import_tilespecs(outstack,tilespecs, render=self.render)
                renderapi.stack.set_stack_state(outstack,'COMPLETE',render=self.render)
 

              

        # out_d ={
        #     'output_stacks':output_stacks,
        #     'output_split_k':self.args['output_split_k'],
        #     'rows':rows,
        #     'columns':cols     
        # }
        # self.output(out_d)

if __name__ == '__main__':
    mod = SplitStack(input_data = example_input)
    mod.run()
