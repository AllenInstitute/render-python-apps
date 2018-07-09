import argschema
import numpy as np
from shapely import geometry,ops
import renderapi
from skimage import measure
from skimage.morphology import watershed
from scipy import ndimage as ndi
import tifffile
from renderapps.module.render_module import RenderModule, RenderParameters
from renderapps.TrakEM2.AnnotationJsonSchema import AnnotationFile
import json


def make_point_box(xy,box_size):
    x=xy[0]
    y=xy[1]
    pts = np.array([[x,y],[x+box_size,y],[x+box_size,y+box_size],[x,y+box_size]])
    return geometry.Polygon(pts)

def make_coords_to_geom(coors,box_size):
    polys = [make_point_box([c[0],c[1]],box_size) for c in coors]
    return ops.cascaded_union(polys)

def make_area_from_polygon(polygon,pixel_size,xoffset,yoffset,z):
    assert(type(polygon) is geometry.Polygon)
    x,y = polygon.exterior.xy
    x=np.array(x)
    y=np.array(y)
    x*=pixel_size
    x+=xoffset
    y*=pixel_size
    y+=yoffset
    xy = np.stack([x,y]).T
    d={'z':z,'global_path':xy}
    return d

def make_prop_into_contours(prop,pixel_size,xoffset=0,yoffset=0,zoffset=0):
    coors = np.flip(np.copy(prop.coords),1)
    zvalues = np.unique(coors[:,2])
    polys=[]
    areas = []
    for z in zvalues:
        c2 = coors[coors[:,2]==z]
        multipoly = make_coords_to_geom(c2,1.0)
        if type(multipoly) is geometry.MultiPolygon:
            for g in multipoly.geoms:
                areas.append(make_area_from_polygon(g,pixel_size,xoffset,yoffset,z+zoffset))
        else:
            areas.append(make_area_from_polygon(multipoly,pixel_size,xoffset,yoffset,z+zoffset))
                 
    return areas   



def segment_syn_prop_map(syn_prop_map,threshold_high = .5, threshold_low = .05):
    low_mask = syn_prop_map>threshold_low
    labels = ndi.label(low_mask)[0]
    props = measure.regionprops(labels,intensity_image=syn_prop_map)
    for prop in props:
        if(prop.max_intensity<threshold_high):
            labels[prop.coords[:,0],prop.coords[:,1],prop.coords[:,2]]=0
    print("before filtering:",len(props))
    props = measure.regionprops(labels)
    print("after filtering:",len(props))
    return labels,props

example_parameters= {
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":8988,
        "owner":"Forrest",
        "project":"M247514_Rorb_1",
        "client_scripts":"/nas4/getVolume/render/render-ws-java-client/src/main/scripts",
        "memGB":"5g"
    },
    "syn_probability_file":"/nas3/data/M247514_Rorb_1/processed/Take2Site4AlignStacks/glut_synapses15a.tiff",
    "output_file":"/nas3/data/M247514_Rorb_1/processed/Take2Site4AlignStacks/glut_synapses15a_global.json",
    "stack_for_bounds":"Take2Site4Align_EMclahe",
    "segment_tiff":"/nas3/data/M247514_Rorb_1/processed/Take2Site4AlignStacks/glut_synapses15a_labels.tiff"
}
# example_parameters= {
#     "render":{
#         "host":"ibs-forrestc-ux1",
#         "port":8988,
#         "owner":"Forrest",
#         "project":"M247514_Rorb_1",
#         "client_scripts":"/nas4/getVolume/render/render-ws-java-client/src/main/scripts",
#         "memGB":"5g"
#     },
#     "syn_probability_file":"/nas3/data/M247514_Rorb_1/processed/Site3AlignStacks/glut_synapses14b.tiff",
#     "output_file":"/nas3/data/M247514_Rorb_1/processed/Site3AlignStacks/glut_synapses14b_global.json",
#     "stack_for_bounds":"Site3Align2_EM_clahe_mm",
#     "segment_tiff":"/nas3/data/M247514_Rorb_1/processed/Site3AlignStacks/glut_synapses14b_labels.tiff"
# }
class SegmentSynapsesParameters(RenderParameters):
    scale = argschema.fields.Float(default=.03,description="renderScale to save")
    stack_for_bounds = argschema.fields.Str(required=True,description="stack to get bounds from")
    syn_probability_file = argschema.fields.InputFile(required=True, description="path to probability map")
    output_file = argschema.fields.OutputFile(required=True,description="path to save segmentation results")
    threshold_high = argschema.fields.Float(required=False,default=.25,description="high threshold for segm.")
    threshold_low = argschema.fields.Float(required=False,default=.065,description="low threshold for segm.")
    segment_tiff = argschema.fields.OutputFile(required=False,description="path to save label tiff")
    
class SegmentSynapses(RenderModule):
    default_schema = SegmentSynapsesParameters
    
    def run(self):
        bounds = renderapi.stack.get_stack_bounds(self.args['stack_for_bounds'],render=self.render)
        pixel_size = 1.0/self.args['scale']
        prop_map = tifffile.imread(self.args['syn_probability_file'])
        labels,props = segment_syn_prop_map(prop_map,
                                      threshold_high=self.args['threshold_high'],
                                      threshold_low=self.args['threshold_low'])
        area_lists = []
        for k,prop in enumerate(props):
            areas=make_prop_into_contours(prop,
                                          pixel_size,
                                          bounds['minX'],
                                          bounds['minY'],
                                          bounds['minZ'])
            area_lists.append({'oid':prop.label,'id':k,'areas':areas})
        d={'area_lists':area_lists}
        schema = AnnotationFile()
        results,errors = schema.dump(d)
        assert(len(errors)==0)
        with open(self.args['output_file'],'w') as fp:
            json.dump(results,fp)
        if self.args.get('segment_tiff',None) is not None:
            with open(self.args['segment_tiff'],'w') as fp:
                tifffile.imsave(fp,labels)

if __name__ == '__main__':
    mod = SegmentSynapses(input_data=example_parameters)
    mod.run()