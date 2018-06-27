import renderapi
import json
import numpy as np
from functools import partial
import os
import pathos.multiprocessing as mp
from shapely import geometry
from ..module.render_module import RenderModule, RenderParameters
from argschema.fields import Str, InputDir, Int

example_json = {
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":80,
        "owner":"Small_volumes_2018",
        "project":"M367240_D_SSTPV_smallvol",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    "stack":"BIG_ROT_FA12_RA00_STI_DCV_FF_Session1",
    #"polygon_dir":"/nas3/data/M247514_Rorb_1/processed/shape_polygons",
    "minX": 0,
    "minY": 0,
    "maxX": 10,
    "maxY": 10,
    "matchcollection":"M367240_D_SSTPV_smallvol_DAPI_1_3D_v9_r0",
    "targetmatchcollection":"M367240_D_SSTPV_smallvol_DAPI_1_3D_v9_r0_FIL"
}



class FilterPointMatchParameters(RenderParameters):
    stack = Str(required=True,
        description='stack sectionPolygons are based upon')

    minX = Int(required=True,
        description='MinX')
    minY = Int(required=True,
        description='MinY')
    maxX = Int(required=True,
        description='MaxX')
    maxY = Int(required=True,
        description='MaxY')

    matchcollection = Str(required=True,
        description='match collection to filter')

    targetmatchcollection = Str(required=True,
        description='match collection to output to')

def mask_points(points,mask):
    p = np.array(points).T
    return p[mask,:].T.tolist()

def mask_match(match,mask):
    if np.sum(mask)==0:
        return None
    match['matches']['p']=mask_points(match['matches']['p'],mask)
    match['matches']['q']=mask_points(match['matches']['q'],mask)
    w = np.array(match['matches']['w'])
    match['matches']['w']=w[mask].tolist()
    return match

def find_inside_points(r,stack,matchp,ts,poly):
    local_points=np.array(matchp).T
    world_points = r.run(renderapi.coordinate.local_to_world_coordinates_array,stack,local_points,ts.tileId,ts.z)
    worldPoints = [geometry.Point(x,y) for x,y in world_points]
    isInside = map(lambda x: x.within(poly),worldPoints)
    return np.array(isInside)

def filter_match(r,match,stack,polyp,polyq,tsp,tsq):
    insidep = find_inside_points(r,stack,match['matches']['p'],tsp,polyp)
    insideq = find_inside_points(r,stack,match['matches']['q'],tsq,polyq)
    insideboth = insidep & insideq
    newmatch = mask_match(match,insideboth)
    return newmatch

def filter_matches(r,stack,fromcollection,tocollection,polydict,pgroup):
    matches=r.run(renderapi.pointmatch.get_matches_with_group,fromcollection,pgroup)
    new_matches = []
    try:
        polyp = polydict[pgroup]
        z = r.run(renderapi.stack.get_z_value_for_section,stack,pgroup)
        tilespecs = r.run(renderapi.tilespec.get_tile_specs_from_z,stack,z)
        tiledict = {}
        for ts in tilespecs:
            tiledict[ts.tileId]=ts
        qgroups = set([match['qGroupId'] for match in matches])

        for qgroup in qgroups:
            z = r.run(renderapi.stack.get_z_value_for_section,stack,qgroup)
            tilespecs=r.run(renderapi.tilespec.get_tile_specs_from_z,stack,z)
            for ts in tilespecs:
                tiledict[ts.tileId]=ts
        for match in matches:
            qgroup = match['pGroupId']
            polyq = polydict[qgroup]
            new_match = filter_match(r,match,stack,polyp,polyq,tiledict[match['pId']],tiledict[match['qId']])
            if new_match is not None:
                new_matches.append(match)
        #print(json.dumps(new_matches))
        #print tocollection
        renderapi.pointmatch.import_matches(tocollection,new_matches,render=r)

        #return r.run(renderapi.pointmatch.import_matches,tocollection,json.dumps(new_matches))
    except:
        print "Exception"


def create_polydict(r,stack,mask_dir):
    sectionData=r.run(renderapi.stack.get_sectionData_for_stack,stack)
    sectionIds=[sd['sectionId'] for sd in sectionData]
    polydict = {}
    for sectionId in sectionIds:
        z = r.run(renderapi.stack.get_z_value_for_section,stack,sectionId)
        polyfile = os.path.join(mask_dir,'polygon_%05d.json'%z)
        polyjson = json.load(open(polyfile,'r'))
        poly = geometry.shape(polyjson['roi'])
        polydict[sectionId]=poly
    return polydict

def create_polydict_coords(r,stack,minX,minY,maxX,maxY):
    #sectionData=r.run(renderapi.stack.get_sectionData_for_stack,stack)
    sectionData = renderapi.stack.get_stack_sectionData(stack,render=r)
    sectionIds=[sd['sectionId'] for sd in sectionData]
    polydict = {}
    for sectionId in sectionIds:
        z = r.run(renderapi.stack.get_z_value_for_section,stack,sectionId)
        #polyfile = os.path.join(mask_dir,'polygon_%05d.json'%z)
        #polyjson = json.load(open(polyfile,'r'))
        #poly = geometry.shape(polyjson['roi'])
        poly = geometry.box(minX,minY,maxX,maxY)
        polydict[sectionId]=poly
    return polydict

def create_zdict(r,stack):
    #sectionData=r.run(renderapi.stack.get_sectionData_for_stack,stack)
    sectionData = renderapi.stack.get_stack_sectionData(stack,render=r)
    sectionIds=[sd['sectionId'] for sd in sectionData]
    zdict={}
    for sectionId in sectionIds:
        z = r.run(renderapi.stack.get_z_value_for_section,stack,sectionId)
        zdict[sectionId]=z
    return zdict

class FilterPointMatch(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = FilterPointMatchParameters
        super(FilterPointMatch,self).__init__(schema_type=schema_type,*args,**kwargs)
    def run(self):
        #self.logger.error("WARNING NOT TESTED, TALK TO FORREST IF BROKEN OR WORKS")

        stack = self.args['stack']
        #polygonfolder = self.args['polygon_dir']
        matchcollection = self.args['matchcollection']
        targetmatchcollection =self.args['targetmatchcollection']
        minX = self.args['minX']
        minY = self.args['minY']
        maxX = self.args['maxX']
        maxY = self.args['maxY']

        #define a dictionary of z values for each sectionId
        zdict = create_zdict(self.render,stack)

        #define a dictionary of polygons for each sectionId
        polydict = create_polydict_coords(self.render,stack,minX,minY,maxX,maxY)

        #get the set of starting sectionIds for the point match database
        pgroups = self.render.run(renderapi.pointmatch.get_match_groupIds_from_only,matchcollection)

        #define a partial function on filter_matches that takes in a single sectionId
        mypartial=partial(filter_matches,self.render,stack,matchcollection,targetmatchcollection,polydict)

        #res = pool.map(mypartial,pgroups)
        for pgroup in pgroups:
            mypartial(pgroup)

if __name__ == "__main__":
    mod = FilterPointMatch(input_data= example_json)
    mod.run()
