import pandas as pd
import numpy as np
from renderapi.tilespec import AffineModel
import renderapi
import json
import os
from functools import partial
import argparse
from renderapi.utils import stripLogger
example_json={
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":8080,
        "owner":"Forrest",
        "project":"M247514_Rorb_1",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    "stack":"REGFLATSMALLFIXDAPI_1_deconv"
}
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = "import xml files for each Z to register EM to LM")
    parser.add_argument('--inputJson',help='json based input argument file',type=str)
    parser.add_argument('--verbose','-v',help='verbose logging',action='store_true')
    args = parser.parse_args()
    jsonargs = json.load(open(args.inputJson,'r'))

    if args.inputJson is None:
        jsonargs = example_json
    else:
        jsonargs = json.load(open(args.inputJson,'r'))
    if args.verbose:
        stripLogger(logging.getLogger())
        logging.basicConfig(level=logging.DEBUG,stream=sys.stdout)
        logging.debug('verbose mode enabled!')

    stack = jsonargs['stack']
    outstack=stack+ '_CONS'
    r = renderapi.Render(**jsonargs['render'])
    json_dir = '/nas3/data/%s/processed/consolidated_affine_json/'%(jsonargs['render']['project'])
    if not os.path.isdir(json_dir):
        os.makedirs(json_dir)

    import pathos.multiprocessing as mp
    pool =mp.ProcessingPool(20)

    zvalues=r.run(renderapi.stack.get_z_values_for_stack,stack)

    def process_z_make_json(r,json_dir,z,verbose=False):
        def consolidate_transforms(tforms,verbose=False,makePolyDegree=0):
            
            if verbose:
                points = np.array([[0,0],[1000,1000]])
                print 'consolidate_transforms:before 0,0 maps to'
                for tform in tforms:
                    points = tform.tform(points)
                    print tform.M
                print points
                

            tform_total = AffineModel()
            start_index = 0
            total_affines = 0
            new_tform_list = []
          
            for i,tform in enumerate(tforms):
                if 'AffineModel2D' in tform.className:
                    total_affines+=1    
                    tform_total = tform.concatenate(tform_total)
                    #tform_total.M=tform.M.dot(tform_total.M)
                else:
                    if verbose:
                        print 'non affine',tform
                    if total_affines>0:
                        if makePolyDegree>0:
                            polyTform = Polynomial2DTransform()._fromAffine(tform_total)
                            polyTform=polyTform.asorder(makePolyDegree)
                            new_tform_list.append(polyTform)
                        else:
                            new_tform_list.append(tform_total)
                        tform_total = AffineModel()
                        total_affines =0
                    new_tform_list.append(tform)
            if total_affines>0:
                if makePolyDegree>0:
                    polyTform = Polynomial2DTransform()._fromAffine(tform_total)
                    polyTform=polyTform.asorder(makePolyDegree)
                    new_tform_list.append(polyTform)
                else:
                    new_tform_list.append(tform_total)
            
            if verbose:
                points = np.array([[0,0],[1000,1000]])
                print 'consolidate_transforms: after 0,0 maps to '
                for tform in new_tform_list:
                    points = tform.tform(points)
                print points
                print 'tforms after',new_tform_list
            return new_tform_list
        
        tilespecs = r.run(renderapi.tilespec.get_tile_specs_from_z,stack,z)
       
        for ts in tilespecs: 
            if verbose:
                print ts.tileId
            ts.tforms = consolidate_transforms(ts.tforms,verbose)   
            if verbose:
                print 'consolidated tformlist'
                print ts.tforms[0].M
                
        if verbose:
            print tilespecs[0].tileId,tilespecs[0].tforms
        json_filepath = os.path.join(json_dir,'%s_%04d'%(outstack,z))
        renderapi.utils.renderdump(tilespecs,open(json_filepath,'w'),indent=4)
        return json_filepath
            
    json_files=pool.map(partial(process_z_make_json,r,json_dir),zvalues)

    r.run(renderapi.stack.delete_stack,outstack)
    r.run(renderapi.stack.create_stack,outstack,verbose=True)
    r.run(renderapi.client.import_jsonfiles_parallel,outstack,json_files)
