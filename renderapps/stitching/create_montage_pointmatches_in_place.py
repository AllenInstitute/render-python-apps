import numpy as np
from renderapi.transform import AffineModel
import renderapi
import json
import os
from functools import partial
import numpy as np
import time
import subprocess
from ..module.render_module import RenderModule,RenderParameters
import marshmallow as mm

example_parameters={
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":8080,
        "owner":"S3_Run1",
        "project":"S3_Run1_Jarvis",
        "client_scripts":"/var/www/render/render-ws-java-client/src/main/scripts"
    },
    "stack":"Stitched_DAPI_1_dropped",
    "matchCollection":"S3_Run1_Jarvis_68_to_112_DAPI_1_highres_2D_75",
    "minZ":6800,
    "maxZ":11299,
    "delta":75,
    "dataRoot":"/nas2/data/"
}

class CreateMontagePointMatchParameters(RenderParameters):
    stack = mm.fields.Str(required=True,
        metadata={'description':'stack to take stitching from'})
    matchCollection = mm.fields.Str(required=True,
        metadata={'description':'collection to save to'})
    minZ = mm.fields.Int(required=False,
        metadata={'description':'min Z to consider'})
    maxZ = mm.fields.Int(required=False,
        metadata={'description':'min Z to consider (default min in stack)'})
    dataRoot = mm.fields.Str(required = True,
        metadata={'description':'max Z to consider (default max in stack)'})
    delta = mm.fields.Int(required=False,default=150,
        metadata ={'description':'number of pixels between artificial matches'})
    pool_size = mm.fields.Int(required=False,default=20,
        metadata={'description':'number of parallel processes (default 20)'})

def make_tile_pair_json(r,stack,project,owner,host,port,json_dir,z):
    tile_json_pair_path=os.path.join(json_dir,'in_section_pairs_%s_z%04d.json'%(stack,z))
    args = ['--stack',stack,
                '--project',project,
                '--owner',owner,
                '--baseDataUrl','%s:%d/render-ws/v1'%(host,port),
                '--zNeighborDistance','%d'%0,
                '--toJson',tile_json_pair_path,
                '--xyNeighborFactor','%3.2f'%.5,
                '--minZ','%d'%z,
                '--maxZ','%d'%z]
    renderapi.client.call_run_ws_client('org.janelia.render.client.TilePairClient',args,renderclient=r,subprocess_mode=subprocess.call)
    return tile_json_pair_path

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
        if not poly_int.is_empty:
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
    print "Putting %d pairs in %s"%(len(pairs),matchcollection)


class CreateMontagePointMatch(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = CreateMontagePointMatchParameters
        super(CreateMontagePointMatch,self).__init__(schema_type=schema_type,*args,**kwargs)
    def run(self):
        print mod.args

        stack = self.args['stack']
        json_dir = os.path.join(self.args['dataRoot'],
            '%s/processed/point_match_in_place'%self.args['render']['project'])

        if not os.path.isdir(json_dir):
            os.makedirs(json_dir)

        #figure out what z values to visit
        zvalues = self.render.run(renderapi.stack.get_z_values_for_stack,stack)
        minZ = self.args.get('minZ',np.min(zvalues))
        maxZ = self.args.get('maxZ',np.max(zvalues))
        zvalues = np.array(zvalues)
        zvalues = zvalues[zvalues>minZ]
        zvalues = zvalues[zvalues<maxZ]

        kwargs = self.render.make_kwargs()
        make_tile_part = partial(make_tile_pair_json,self.render,self.args['stack'],kwargs['project'],kwargs['owner'],kwargs['host'],kwargs['port'],json_dir)
        with renderapi.client.WithPool(self.args['pool_size']) as pool:
            tile_pair_jsons=pool.map(make_tile_part,zvalues)
        #for z in zvalues:
        #    make_tile_part(z)


        print "Done with tile pairs, now creating matches!"
        print tile_pair_jsons

        myp = partial(process_tile_pair_json_file,
            self.render,
            self.args['matchCollection'],
            self.args['stack'],
            self.args['render']['owner'],
            delta=self.args['delta'])
        with renderapi.client.WithPool(self.args['pool_size']) as pool:
            res=pool.map(myp,tile_pair_jsons)
        #for tile_pair in tile_pair_jsons:
            #print tile_pair
            #myp(tile_pair)
            #break

if __name__ == "__main__":
    mod = CreateMontagePointMatch(input_data=example_parameters)
    #mod = CreateMontagePointMatch(schema_type=CreateMontagePointMatchParameters)
    mod.run()
