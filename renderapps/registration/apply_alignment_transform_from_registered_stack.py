import renderapi
import numpy as np
from functools import partial
import os
import pathos.multiprocessing as mp
from shapely import geometry
import logging
from renderapi.transform import AffineModel
from renderapps.module.render_module import RenderModule,RenderParameters


example_json = {
        "render":{
            "host":"ibs-forrestc-ux1",
            "port":8080,
            "owner":"Forrest",
            "project":"M247514_Rorb_1",
            "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
        },
        "prealignedstack":"REGFLATDAPI_1_deconvnew",
        "postalignedstack":"ALIGN2_MARCH24b_DAPI_1_deconvnew",
        "source_stack":"EM_reg2",
        "output_stack":"ALIGN2_MARCH24c_EM_reg2",
        "pool_size":20,
        "stackResolutionX":1,
        "stackResolutionY":1,
        "stackResolutionZ":1
}

class ApplyAlignmentFromRegisteredStackParametersBase(RenderParameters):
    prealigned_stack = mm.fields.Str(required=True,
        metadata={'description':'stack has same tiles as aligned stack but is registered with source_stack(s) example'})
    postaligned_stack = mm.fields.Str(required=True,
        metadata={'description':'stack has same tiles as prealignedstack stack but is in the desired aligned space'})
    pool_size = mm.fields.Int(required=False,default=20,
        metadata={'description':'degree of parallelism (default 20)'})
    stackResolutionX = mm.fields.Int(required=False,default=1,
        metadata={'description':'X stack resolution (nm)  to save in output stack (default use source stack)'})
    stackResolutionY = mm.fields.Int(required=False,default=1,
        metadata={'description':'Y stack resolution (nm)  to save in output stack (default use source stack)'})
    stackResolutionZ = mm.fields.Int(required=False,default=1,
        metadata={'description':'Z stack resolution (nm) to save in output stack (default use source stack)'})

class ApplyAlignmentFromRegisteredStackParameters(ApplyAlignmentFromRegisteredStackParametersBase):
    source_stack = mm.fields.Str(required=True,
        metadata={'description':'stack that is registered with prealignedstack, but which you want to re-express in the space of postalignedstack'})
    output_stack = mm.fields.Str(required=True,
        metadata={'description':'name to call output stack version of source stack'})

logger = logging.getLogger(__name__)


def define_local_grid(ts, num_points):
    xvals = np.linspace(0, ts.width-1, num=num_points, endpoint=True)
    yvals = np.linspace(0, ts.height-1, num=num_points, endpoint=True)
    (xx,yy) = np.meshgrid(xvals, yvals)
    #unravel the grid and make it a Nx2 matrix of x,y columns
    xy = np.vstack([xx.ravel(), yy.ravel()]).T
    return xy

def process_z(r,prealignedstack,postalignedstack,sourcestack,outstack,z,num_points = 4):

    ts_source = r.run(renderapi.tilespec.get_tile_specs_from_z, sourcestack,z)

    final_list = []

    start_index = 0

    index_dict = {}
    #loop over the source tilespecs to figure out where they each go
    for ts in ts_source:

        #define a grid of local coordinates across the source tile
        xy_local_source = define_local_grid(ts, num_points)

        #map those local coordinates to the registered world coordinates
        xy_local_source_json = renderapi.coordinate.package_point_match_data_into_json(xy_local_source, ts.tileId, 'local')

        #package them into a list of lists for batch processing
        for elem in xy_local_source_json:
            final_list.append([elem])
        end_index = start_index+len(xy_local_source_json)
        #keep track of where in the final_list these coordinates are to pull out later
        index_dict[ts.tileId] = {'start_index':start_index, 'end_index':end_index}

        start_index = end_index
        #final_list.append(temp_list)

    #map all those local coordinates into world coordinates of the registered source stack
    xy_world_reg = r.run(renderapi.coordinate.local_to_world_coordinates_clientside, sourcestack, final_list, z, number_of_threads=3)

    #map those world coordinates to the local coordinates of the prealigned stack
    xy_local_prealigned_json = r.run(renderapi.coordinate.world_to_local_coordinates_clientside, prealignedstack,xy_world_reg, z, number_of_threads=3)

    #map those local coordinates to the world coordinates of the postaligned stack
    xy_world_postaligned_json = r.run(renderapi.coordinate.local_to_world_coordinates_clientside, postalignedstack, xy_local_prealigned_json, z, number_of_threads=3)

    #replace the transform for this tile with that transformation
    for ts in ts_source:
        xy_local_source = define_local_grid(ts, num_points)
        start = index_dict[ts.tileId]['start_index']
        end = index_dict[ts.tileId]['end_index']
        #pull out the correct elements of the list

        registered_world_coords = xy_world_reg[start:end]
        aligned_world_coords_json = xy_world_postaligned_json[start:end]
        #packaged them into an numpy array

        good_aligned_world_coords = [c for c in aligned_world_coords_json if 'error' not in c.keys()]
        aligned_world_coords = renderapi.coordinate.unpackage_local_to_world_point_match_from_json(good_aligned_world_coords)
        #fit a polynomial tranformation
        tform = AffineModel()
        notError = np.array([('error' not in d.keys()) for d in aligned_world_coords_json])
        tform.estimate(xy_local_source[notError, :], aligned_world_coords)
        ts.tforms = [tform]
        logger.debug('from,to')
        for frompt, topt in zip(registered_world_coords, aligned_world_coords_json):
            logger.debug((frompt, topt))
        #break

    r.run(renderapi.client.import_tilespecs,outstack,ts_source)
    return None

class ApplyAlignmentFromRegisteredStack(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = ApplyAlignmentFromRegisteredStacksParameters
        super(ApplyAlignmentFromRegisteredStack,self).__init__(schema_type=schema_type,*args,**kwargs)
    def run(self):
        self.logger.error('WARNING NEEDS TO BE TESTED, TALK TO FORREST IF BROKEN')

        prealignedstack = self.args['prealigned_stack']
        postalignedstack = self.args['postaligned_stack']
        sourcestack = self.args['source_stack']
        stackMetadata = renderapi.stack.get_stack_metadata(sourcestack,render=self.render)
        stackResolutionX = self.args.get('stackResolutionX',sourcestack['stackResolutionX'])
        stackResolutionY = self.args.get('stackResolutionY',sourcestack['stackResolutionY'])
        stackResolutionZ = self.args.get('stackResolutionZ',sourcestack['stackResolutionZ'])

        pool = mp.ProcessPool(self.args['pool_size'])

        outstack = self.args[output_stack]
        myp = partial(process_z, self.render, prealignedstack, postalignedstack, sourcestack, outstack)
        zvalues = self.render.run(renderapi.stack.get_z_values_for_stack, sourcestack)

        self.render.run(renderapi.stack.delete_stack, outstack)
        self.render.run(renderapi.stack.create_stack, outstack,
            stackResolutionX = stackResolutionX,
            stackResolutionY = stackResolutionY,
            stackResolutionZ = stackResolutionZ)

        #for z in zvalues:
        #    myp(z)
        #    break
        res = pool.map(myp, zvalues)
        #self.render.run(renderapi.stack.set_stack_state,outstack,state='COMPLETE')
        #break

if __name__ == "__main__":
    mod = ApplyAlignmentFromRegisteredStack(input_data= example_json)
    mod.run()


