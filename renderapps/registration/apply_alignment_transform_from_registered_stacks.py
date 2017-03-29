import renderapi
import json
import numpy as np
from functools import partial
import os
import pathos.multiprocessing as mp
from shapely import geometry
import argparse 
from renderapi.utils import stripLogger
import logging
import sys
from renderapi.transform import AffineModel
from renderapps.module.RenderModule import RenderModule

logger = logging.getLogger(__name__)


# "registered_stacks":["EM_reg",
#                     "REGFLATMBP_deconv",
#                     "REGFLATDAPI_1_deconv",
#                     "REGFLATDAPI_2_deconv",
#                     "REGFLATDAPI_3_deconv",
#                     "REGFLATGABA_deconv",
#                     "REGFLATGAD2_deconv",
#                     "REGFLATGluN1_deconv",
#                     "REGFLATPSD95_deconv",
#                     "REGFLATTdTomato_deconv",
#                     "REGFLATVGlut1_deconv",
#                     "REGFLATsynapsin_deconv"],

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

    
class ApplyAlignmentFromRegisteredStacks(RenderModule):
    def __init__(self, parser, *args,**kwargs):

        RenderModule.__init__(self,parser,*args,**kwargs)

    def run(self):
        prealignedstack = self.args['prealignedstack']
        postalignedstack = self.args['postalignedstack']
        pool = mp.ProcessPool(20)
        #loop over the target stacks
        for sourcestack in self.args['registered_stacks']:
            outstack = sourcestack.replace(self.args['oldprefix'], '')
            outstack = self.args['newprefix']+outstack
            myp = partial(process_z, self.render, prealignedstack, postalignedstack, sourcestack, outstack)
            zvalues = self.render.run(renderapi.stack.get_z_values_for_stack, sourcestack)
            self.render.run(renderapi.stack.delete_stack, outstack)
            self.render.run(renderapi.stack.create_stack, outstack, stackResolutionX = 3, stackResolutionY = 3, stackResolutionZ = 70)
            #for z in zvalues:
            #    myp(z)
            #    break
            res = pool.map(myp, zvalues)
            #self.render.run(renderapi.stack.set_stack_state,outstack,state='COMPLETE')
            #break
 
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = "Filter point matches that start or end outside polygons defined in polygon_dir,\
    that were generated from specified stack")

    example_json = {
        "render":{
            "host":"ibs-forrestc-ux1",
            "port":8080,
            "owner":"Forrest",
            "project":"M247514_Rorb_1",
            "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
        },
        "prealignedstack":"REG_MARCH_21_DAPI_1",
        "postalignedstack":"ALIGN2_MARCH_24b_DAPI_1",
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
        "oldprefix":"REG_MARCH_21_",
        "newprefix":"ALIGN2_MARCH24b_"
    }
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
        "registered_stacks":["EM_reg2"],
        "oldprefix":"REG_MARCH_21_",
        "newprefix":"ALIGN2_MARCH24b_"
    }
    module = ApplyAlignmentFromRegisteredStacks(parser, example_json=example_json)
    module.run()
