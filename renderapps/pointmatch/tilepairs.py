import renderapi.stack
from ..shapely import tilespec_to_bounding_box_polygon
import marshmallow as mm

class Tile(mm.Schema):
    groupId = mm.fields.Str(required=True)
    id = mm.fields.Str(required=True)
class TilePair(mm.Schema):
    p = mm.fields.Nested(Tile, required=True)
    q = mm.fields.Nested(Tile, required=True)
class TilePairFile(mm.Schema):
    renderParametersUrlTemplate = mm.fields.Str(required=True)
    neighborPairs = mm.fields.Nested(TilePair,many=True)


def find_tile_pair_match_in_z(render,stack,p,p_geom,z2,minx,miny,width,height,overlap_frac=.25):
    pairs = []
    paired = render.run(renderapi.tilespec.get_tile_specs_from_box,stack,z2,minx,miny,width,height)
    for ts2 in paired:
        ts2_geom = tilespec_to_bounding_box_polygon(ts2)
        overlap = ts_geom.intersection(ts2_geom)
        frac_overlap = overlap.area/ts_geom.area
        if frac_overlap > area_overlap_frac:
            q = {}
            q['id']=ts2.tileId
            q['groupId']=ts2.layout.sectionId
            pair = {'p':p,'q':q}
            pairs.append(pair)
    return pairs

def define_box_and_geometry(ts,radius):
    ts_geom = tilespec_to_bounding_box_polygon(ts)
    width = ts.width*(1+2*radius)
    height = ts.height*(1+2*radius)
    minx = ts.minX - ts.width*radius
    miny = ts.minY - ts.width*radius
    p = {}
    p['id']=ts.tileId
    p['groupId']=ts.layout.sectionId
    return ts_geom,width,height,minx,miny,p

def find_tile_pairs_in_radius(render,stack,ts,z,dz,radius,area_overlap_frac=.25):
    pairs = []
    ts_geom,width,height,minx,miny,p = define_box_and_geometry(ts,radius)

    for z2 in range(z-dz,z+dz+1):
        if (z!=z2):
            pairs += find_tile_pair_match_in_z(render,stack,p,ts_geom,z2,minx,miny,width,height,overlap_frac)
        
    return pairs

def make_template_url(owner,project,stack,queryParameters={}):

    template_url = "{baseDataUrl}/owner/{owner}}/project/{project}/stack/{stack}/tile/{id}/render-parameters"
    template_url = template_url.replace("{owner}",owner)
    template_url = template_url.replace("{project}",project)
    template_url = template_url.replace("{stack}",stack)
    template_url +="?"+"&".join(["%s=%s"%(key,value) for key,value in queryParameters.iteritems()])
    return template_url

def format_pairfile(render,stack,pairs,queryParameters={}):
    pairfile = {}
    template_url = make_template_url(render.DEFAULT_OWNER,render.DEFAULT_PROJECT,stack,queryParameters)
    pairfile['renderParametersUrlTemplate'] = template_url
    pairfile['neighborPairs']=pairs

    return pairfile

def create_tile_pair_for_single_z(render,stack,z,dz=10,radius=.1,pool_size=20,queryParameters={},overlap_frac=.25):
    tilespecs = render.run(renderapi.tilespec.get_tile_specs_from_z,stack,z)
    
    pairs = []
    for ts in tilespecs:            
        pairs+=find_tile_pairs_in_radius(render,stack,ts,z,dz,radius,overlap_frac)

    return format_pairfile(render,stack,pairs,queryParameters)

def create_tile_pair_across_z_break(render,stack,z,dz=10,radius=.1,pool_size=20,queryParameters={},overlap_frac=.25):
    pairs = []
    for z1 in range(z-dz,z+1):
        tilespecs = render.run(renderapi.tilespec.get_tile_specs_from_z,stack,z1)
        for ts in tilespecs:
            p_geom,width,height,minx,miny,p = define_box_and_geometry(ts,radius)
            for z2 in range(z1,z1+dz+1):
                if (z2 > z):
                    pairs += find_tile_pair_match_in_z(render,stack,p,p_geom,z2,minx,miny,width,height,overlap_frac)

    return format_pairfile(render,stack,pairs,queryParameters)


