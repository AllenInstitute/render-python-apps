import pandas as pd
import numpy as np
from renderapi.tilespec import AffineModel
import renderapi
import json
import os
from functools import partial
import argparse
import numpy as np
import time
import subprocess
import tempfile
from renderapi.utils import stripLogger
import logging
import sys


example_json={
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":8080,
        "owner":"Forrest",
        "project":"M247514_Rorb_1",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    "stack":"REGFLATDAPI_1_deconv",
    "matchcollection":"M247514_Rorb_1_DAPI1_deconv",
    "dz":10,
    "minZ":0,
    "maxZ":101,
    "dataRoot":"/nas3/data/"
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = "add montage point matches in place given layout of tiles")
    parser.add_argument('--inputJson',help='json based input argument file',type=str)
    parser.add_argument('--verbose','-v',help='verbose logging',action='store_true')
    args = parser.parse_args()

    if args.verbose:
        # strip logger of handlers in case logger is set up within import block
        stripLogger(logging.getLogger())
        logging.basicConfig(level=logging.DEBUG,stream=sys.stdout)
        logging.debug('verbose mode enabled!')

    jsonargs = json.load(open(args.inputJson,'r'))

    stack = jsonargs['stack']

    r = renderapi.render.connect(**jsonargs['render'])
    json_dir = os.path.join(jsonargs['dataRoot'],'%s/processed/point_match_in_place'%jsonargs['render']['project'])
    if not os.path.isdir(json_dir):
        os.makedirs(json_dir)

    import pathos.multiprocessing as mp
    pool =mp.ProcessingPool(20)

    def make_tile_pair_json(r,stack,project,owner,host,port,json_dir,z):


        tile_json_pair_path=os.path.join(json_dir,'in_section_pairs_%s_z%04d.json'%(stack,z))
        args = ['--stack',stack,
                    '--project',project,
                    '--owner',owner,
                    '--baseDataUrl','http://%s:%d/render-ws/v1'%(host,port),
                    '--zNeighborDistance','%d'%0,
                    '--toJson',tile_json_pair_path,
                    '--xyNeighborFactor','%3.2f'%.5,
                    '--minZ','%d'%z,
                    '--maxZ','%d'%z]

        renderapi.client.call_run_ws_client('org.janelia.render.client.TilePairClient',args,renderclient=r,subprocess_mode=subprocess.call)

        return tile_json_pair_path

    zvalues = r.run(renderapi.stack.get_z_values_for_stack,stack)
    kwargs = r.make_kwargs()
    make_tile_part = partial(make_tile_pair_json,r,jsonargs['stack'],kwargs['project'],kwargs['owner'],kwargs['host'],kwargs['port'],json_dir)
    tile_pair_jsons=pool.map(make_tile_part,zvalues)
    #for z in zvalues:
    #    make_tile_part(z)

    def process_tile_pair_json_file(r,matchcollection,stack,owner,tile_pair_json_file,delta=150):
        import json
        from shapely.geometry import box, Polygon
        import shapely
        import time

        def get_world_box(ts):
            qcorners = np.array([[0,0],[0,ts.height],[ts.width,ts.height],[ts.width,0],[0,0]])
            world_corners=r.run(renderapi.coordinate.local_to_world_coordinates_array,stack,qcorners,ts.tileId,ts.z)
            return Polygon(world_corners)
        tile_pair_json = json.load(open(tile_pair_json_file,'r'))['neighborPairs']
        pairs = []

        for pair in tile_pair_json:
            now = time.time()

            qid = pair['q']['id']
            pid = pair['p']['id']
            qts = r.run(renderapi.tilespec.get_tile_spec,stack,qid)
            pts = r.run(renderapi.tilespec.get_tile_spec,stack,pid)

            polyq=get_world_box(qts)
            polyp=get_world_box(pts)


            poly_int = polyp.intersection(polyq)
            poly_int=poly_int.buffer(-10)

            minx,miny,maxx,maxy = poly_int.bounds
            xx,yy = np.meshgrid(np.arange(minx,maxx,delta),np.arange(miny,maxy,delta))
            xx=xx.ravel()
            yy=yy.ravel()
            isin = np.zeros(len(xx),np.bool)
            for i,xytuple in enumerate(zip(xx,yy)):
                x,y = xytuple
                p = shapely.geometry.Point(x,y)
                if poly_int.contains(p):
                    isin[i]=True
                else:
                    isin[i]=False
            xx=xx[isin]
            yy=yy[isin]
            #print 'step2', time.time()-now
            #now = time.time()
            xy = np.stack([xx,yy]).T

            if xy.shape[0]>0:
                int_local_q=renderapi.coordinate.world_to_local_coordinates_array(stack,xy,qts.tileId,qts.z,render=r)
                int_local_p=renderapi.coordinate.world_to_local_coordinates_array(stack,xy,pts.tileId,pts.z,render=r)

                newpair = {}
                newpair['pId']=pid
                newpair['qId']=qid
                newpair['pGroupId']=pair['p']['groupId']
                newpair['qGroupId']=pair['q']['groupId']
                newpair['matches']={}
                newpair['matches']['p']=[int_local_p[:,0].tolist(),int_local_p[:,1].tolist()]
                newpair['matches']['q']=[int_local_q[:,0].tolist(),int_local_q[:,1].tolist()]
                newpair['matches']['w']=np.ones(len(xx)).tolist()
                pairs.append(newpair)
        resp=r.run(renderapi.pointmatch.import_matches,matchcollection,json.dumps(pairs))

    myp = partial(process_tile_pair_json_file,
        r,
        jsonargs['matchcollection'],
        jsonargs['stack'],
        jsonargs['render']['owner'],
        delta=jsonargs['delta'])
    res=pool.map(myp,tile_pair_jsons)
    #for tile_pair in tile_pair_jsons:
    #    print tile_pair
    #    myp(tile_pair)
    #    break
