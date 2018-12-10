if __name__ == "__main__" and __package__ is None:
    __package__ = "renderapps.materialize.make_downsample_image_stack"
import json
import os
import renderapi
from ..module.render_module import RenderModule, RenderParameters
from argschema.fields import InputFile, InputDir, Str, Float, Int
from functools import partial
import glob
import time
import numpy as np
from PIL import Image
from renderapi.transform.leaf import AffineModel
from renderapi.tilespec import TileSpec, Layout
from renderapi.channel import Channel
from renderapi.image_pyramid import MipMap, ImagePyramid
import tifffile





# modified and fixed by Sharmishtaa Seshamani, Leila, tk and Forrest.
example_parameters = {
    "render": {
        "host": "ibs-forrestc-ux1",
        "port": 80,
        "owner": "S3_Run1",
        "project": "S3_Run1_Igor",
        "client_scripts": "/var/www/render/render-ws-java-client/src/main/scripts"
    },
    'input_stack': 'Stitched_DAPI_1_dropped',
    'output_stack': 'Stitched_DAPI_1_Lowres_62_to_67',
    'image_directory': '/nas3/data/S3_Run1_Igor/processed/Low_res',
    'pool_size': 20,
    'scale': 0.05
}


class MakeDownsampleSectionStackParameters(RenderParameters):
    input_stack = Str(required=True,
                      description='stack to make a downsample version of')
    scale = Float(required=False, default=.01,
                  description='scale to make images')
    image_directory = Str(required=True,
                          metadata={'decription', 'path to save section images'})
    numsectionsfile = Str(required=True,
                          metadata={'decription', 'file to save length of sections'})
    output_stack = Str(required=True,
                       metadata={'description': 'output stack to name'})
    pool_size = Int(required=False, default=20,
                    metadata={'description': 'number of parallel threads to use'})
    minZ = Int(required=False, default=0,
               metadata={'description': 'Minimum Z value'})
    maxZ = Int(required=False, default=100000000,
               metadata={'description': 'Maximum Z value'})


def process_z(render, stack, output_dir, scale, project, tagstr, Z):

    z = Z[0]
    newz = Z[1]

    args = ['--stack', stack,
           '--scale', str(scale),
           '--rootDirectory', output_dir,
           str(z)]

    print args
    print project

    #############render.run(renderapi.client.call_run_ws_client, 'org.janelia.render.client.RenderSectionClient', add_args = args)

    stackbounds = renderapi.stack.get_stack_bounds(stack, render=render)
    sectionbounds = renderapi.stack.get_bounds_from_z(stack, z, render=render)

    cx1 = (stackbounds['minX'] - stackbounds['maxX'])/2
    cy1 = (stackbounds['minY'] - stackbounds['maxY'])/2

    cx2 = (sectionbounds['minX'] - sectionbounds['maxX'])/2
    cy2 = (sectionbounds['minY'] - sectionbounds['maxY'])/2

    dx = sectionbounds['minX']
    dy = sectionbounds['minY']

    #bb = renderapi.image.get_bb_image(stack, z, stackbounds['minX'], stackbounds['minY'], width, height, scale, render=render)

    print "This is z: "
    print z
    print "These are stack bounds: "
    print stackbounds
    print "These are section bounds: "
    print sectionbounds

    tilespecdir = os.path.join(output_dir, project, stack, 'sections_at_%s' % str(
        scale), 'tilespecs_%s' % tagstr)
    tilespecdir = os.path.normpath(tilespecdir)
    if os.path.exists(tilespecdir):
        print ("Path Exists: " + tilespecdir)
    else:
        os.makedirs(tilespecdir)

    [q, r] = divmod(z, 1000)
    s = int(r/100)

    directory = os.path.join(output_dir, project, stack,
                             'sections_at_%s' % str(scale), '%03d' % q, "%d" % s)
    directory = os.path.normpath(directory)
    print("checking for: " + directory)
    print(os.path.exists(directory))
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(os.path.exists(directory))
    else:
        print ("did not make directory: " + directory)


    filename = os.path.join(output_dir, project, stack, 'sections_at_%s' % str(
        scale), '%03d' % q, "%d" % s, '%s.tif' % str(z))
    filename = os.path.normpath(filename)
    print("checking for: " + filename)
    print(os.path.isfile(filename))
    if not os.path.isfile(filename):
        renderapi.client.renderSectionClient(stack, output_dir, [z], scale=str(
            scale), render=render, format='tif', doFilter=True, fillWithNoise=False)
        print(os.path.exists(filename))
    else:
        print("Did not make file")

    tilespecs = renderapi.tilespec.get_tile_specs_from_z(
        stack, z, render=render)
    t = TileSpec(tileId=tilespecs[0].tileId, imageUrl=filename, width=stackbounds['maxX']
                 * scale, height=stackbounds['maxY']*scale, minint=0, maxint=255, z=newz, layout=tilespecs[0].layout)
    a = AffineModel(M00=20.0000000000, M01=0.0000000000,
                    M10=0.0000000000, M11=20.0000000000, B0=0.0, B1=0.0)
    ip = ImagePyramid()
    ip[0] = MipMap(imageUrl=filename)
    t.ImagePyramid = ip
    t.tforms = [a]
    allts = [t]
    tilespecfilename = os.path.join(output_dir, project, stack,'sections_at_%s'%str(scale),'tilespecs_%s'%tagstr,'tilespec_%04d.json'%z)
    print tilespecfilename
    fp = open(tilespecfilename, 'w')
    json.dump([ts.to_dict() for ts in allts] , fp, indent=4)
    fp.close()


# @Parameter(names = "--stack", description = "Stack name", required = true)
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
    def __init__(self, schema_type=None, *args,**kwargs):
        if schema_type is None:
            schema_type = MakeDownsampleSectionStackParameters
        super(MakeDownsampleSectionStack, self).__init__(schema_type=schema_type, *args,**kwargs)

    def run(self):
        allzvalues = self.render.run(renderapi.stack.get_z_values_for_stack,
            self.args['input_stack'])

        allzvalues = np.array(allzvalues)
        zvalues = allzvalues[(allzvalues >= self.args['minZ']) & (
            allzvalues <= self.args['maxZ'])]

        tagstr = "%s_%s" %(self.args['minZ'], self.args['maxZ'])

        directoryname = os.path.dirname(self.args['numsectionsfile'])
        if not os.path.isdir(directoryname):
            os.makedirs(directoryname)

        f = open(self.args['numsectionsfile'], 'w')
        f.write("%d" % len(zvalues))
        f.close()

        newzvalues = range(0, len(zvalues))
        Z = []
        for i in range(0, len(zvalues)):
            Z.append([zvalues[i], newzvalues[i]])

        print self.args['input_stack']
        print self.args['pool_size']
        print self.args['image_directory']
        print self.args['scale']
        print newzvalues

        render = self.render
        mypartial = partial(process_z, self.render, self.args['input_stack'],
            self.args['image_directory'], self.args['scale'], self.args['render']['project'],tagstr)
        with renderapi.client.WithPool(self.args['pool_size']) as pool:
            pool.map(mypartial, Z)

        t = os.path.join(self.args['image_directory'], self.args['render']['project'], self.args['input_stack'],'sections_at_%s'%str(self.args['scale']),'tilespecs_%s'%tagstr)
        jsonfiles = glob.glob("%s/*.json" % t)

        renderapi.stack.create_stack(self.args['output_stack'], cycleNumber=5, cycleStepNumber=1,stackResolutionX = 1, stackResolutionY = 1, render=self.render)
        renderapi.client.import_jsonfiles_parallel(self.args['output_stack'], jsonfiles, render=self.render)

if __name__ == "__main__":
    mod = MakeDownsampleSectionStack(
        schema_type=MakeDownsampleSectionStackParameters)

    mod.run()
