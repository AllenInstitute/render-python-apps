if __name__ == "__main__" and __package__ is None:
    __package__ = "renderapps.materialize.make_downsample_image_stack"
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
import time
from PIL import Image
import tifffile

#modified and fixed by Sharmishtaa Seshamani

example_parameters={
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":80,
        "owner":"S3_Run1",
        "project":"S3_Run1_Igor",
        "client_scripts":"/var/www/render/render-ws-java-client/src/main/scripts"
    },
    'input_stack':'Stitched_DAPI_1_dropped',
    'output_stack':'Stitched_DAPI_1_Lowres_62_to_67',
    'image_directory':'/nas3/data/S3_Run1_Igor/processed/Low_res',
    'pool_size':20,
	'scale': 0.05
}

class MakeDownsampleSectionStackParameters(RenderParameters):
    input_stack = mm.fields.Str(required=True,
        metadata={'description':'stack to make a downsample version of'})
    scale = mm.fields.Float(required=False,default = .01,
        metadata={'description':'scale to make images'})
    image_directory = OutputDir(required=True,
        metadata={'decription','path to save section images'})
    numsectionsfile = mm.fields.Str(required=True,
        metadata={'decription','file to save length of sections'})
    output_stack = mm.fields.Str(required=True,
        metadata={'description':'output stack to name'})
    pool_size = mm.fields.Int(required=False,default=20,
        metadata={'description':'number of parallel threads to use'})
    minZ = mm.fields.Int(required=False,default=0,
        metadata={'description':'Minimum Z value'})
    maxZ = mm.fields.Int(required=False,default=100000000,
        metadata={'description':'Maximum Z value'})

def process_z(render,stack,output_dir,scale,project,tagstr,Z):
    
    z = Z[0]
    newz = Z[1]
    
    args=['--stack', stack,
          '--scale',str(scale),
          '--rootDirectory',output_dir ,
          str(z)]
    
    
    print args
    print project
    
    #############render.run(renderapi.client.call_run_ws_client, 'org.janelia.render.client.RenderSectionClient', add_args = args)
    
    
    
    stackbounds = renderapi.stack.get_stack_bounds(stack,render=render)
    sectionbounds = renderapi.stack.get_bounds_from_z(stack,z,render=render)
    
    cx1 = (stackbounds['minX'] - stackbounds['maxX'])/2
    cy1 = (stackbounds['minY'] - stackbounds['maxY'])/2
    
    cx2 = (sectionbounds['minX'] - sectionbounds['maxX'])/2
    cy2 = (sectionbounds['minY'] - sectionbounds['maxY'])/2
    
    dx = sectionbounds['minX']  
    dy = sectionbounds['minY']
    
    #bb = renderapi.image.get_bb_image(stack, z, stackbounds['minX'], stackbounds['minY'], width, height, scale, render=render)
    
    print "This is z: "
    print z
    print "These are stack bounds!"
    print stackbounds
    print "These are section bounds!"
    print sectionbounds
    
    
    tilespecdir = os.path.join(output_dir,project,stack,'sections_at_%s'%str(scale),'tilespecs_%s'%tagstr)
    if os.path.exists(tilespecdir):
		print "Path Exists!" 
    else:
		os.makedirs(tilespecdir)
		
    [q,r] = divmod(z,1000)
    s = int(r/100)
    
    directory = os.path.join(output_dir,project,stack,'sections_at_%s'%str(scale),'%03d'%q,"%d"%s)
    if not os.path.exists(directory):
		os.makedirs(directory)
    #im = Image.fromarray(bb)
    #im.save(filename)
    #tifffile.imsave(filename,bb)
    
    filename = os.path.join(output_dir,project,stack,'sections_at_%s'%str(scale),'%03d'%q,"%d"%s,'%s.tif'%str(z))
    
    if not os.path.isfile(filename):
		renderapi.client.renderSectionClient(stack, output_dir, [z], scale=str(scale), render=render, format='tif', doFilter=False, fillWithNoise=False)
    
    tilespecs = renderapi.tilespec.get_tile_specs_from_z(stack,z,render=render)
    t = tilespecs[0]
    d = t.to_dict()
    d['mipmapLevels'][0]['imageUrl'] = filename
    d['minIntensity'] = 0
    d['maxIntensity'] = 255
    d['width'] = stackbounds['maxX']/20
    d['height'] = stackbounds['maxY']/20
    d['z'] = newz
    d['transforms']['specList'][0]['dataString'] = "20.0000000000 0.0000000000 0.0000000000 20.0000000000 %d %d"%(0.0,0.0)
    #if len(['transforms']['specList']) > 1:
	#	for i in range(1,len(['transforms']['specList'])):
	#		d['transforms']['specList'][i]['dataString'] = "1.0000000000 0.0000000000 0.0000000000 1.0000000000 0000.00 0000.00"
    #d['transforms']['specList'][2]['dataString'] = "1.0000000000 0.0000000000 0.0000000000 1.0000000000 0000.00 0000.00"
    t.from_dict(d) 
    allts = [t]
    tilespecfilename = os.path.join(output_dir,project,stack,'sections_at_%s'%str(scale),'tilespecs_%s'%tagstr,'tilespec_%04d.json'%z)
    print tilespecfilename
    fp = open(tilespecfilename,'w')
    json.dump([ts.to_dict() for ts in allts] ,fp,indent=4)
    fp.close()
    

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

class MakeDownsampleSectionStack(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = MakeDownsampleSectionStackParameters
        super(MakeDownsampleSectionStack,self).__init__(schema_type=schema_type,*args,**kwargs)
    def run(self):
        allzvalues = self.render.run(renderapi.stack.get_z_values_for_stack,
            self.args['input_stack'])
            
        allzvalues = np.array(allzvalues)
        zvalues = allzvalues[(allzvalues >= self.args['minZ']) & (allzvalues <=self.args['maxZ'])]
        
        tagstr = "%s_%s"%(self.args['minZ'],self.args['maxZ'])
        
        f = open(self.args['numsectionsfile'],'w')
        f.write("%d"%len(zvalues))
        f.close()
        
        
        newzvalues = range(0,len(zvalues))
        Z = []
        for i in range(0,len(zvalues)):
			Z.append( [zvalues[i], newzvalues[i]])
        
        print self.args['input_stack']
        print self.args['pool_size']
        print self.args['image_directory']
        print self.args['scale']
        print newzvalues
        #exit(0)
        
        render=self.render
        mypartial = partial(process_z,self.render,self.args['input_stack'],
            self.args['image_directory'],self.args['scale'],self.args['render']['project'],tagstr)
        with renderapi.client.WithPool(self.args['pool_size']) as pool:
            pool.map(mypartial,Z)
            
            
        t = os.path.join(self.args['image_directory'],self.args['render']['project'],self.args['input_stack'],'sections_at_%s'%str(self.args['scale']),'tilespecs_%s'%tagstr) 
        jsonfiles = glob.glob("%s/*.json"%t)    
        
        renderapi.stack.create_stack(self.args['output_stack'],cycleNumber=5,cycleStepNumber=1,stackResolutionX = 1, stackResolutionY = 1, render=self.render)
        renderapi.client.import_jsonfiles_parallel(self.args['output_stack'],jsonfiles,render=self.render)
        #sv = renderapi.stack.get_stack_metadata(self.args['input_stack'], render=self.render)
        #print sv
        #renderapi.stack.set_stack_metadata(self.args['output_stack'], sv, render=self.render)
        #renderapi.stack.set_stack_state(self.args['output_stack'],state='COMPLETE',render=self.render)

if __name__ == "__main__":
    #mod = MakeDownsampleSectionStack(input_data=example_parameters)
    mod = MakeDownsampleSectionStack(schema_type=MakeDownsampleSectionStackParameters)
    
    mod.run()
    
