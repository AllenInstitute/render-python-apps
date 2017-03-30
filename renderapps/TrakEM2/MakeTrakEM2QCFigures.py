import numpy as np
from json_module import JsonModule, ModuleParameters, InputFile
import renderapi
import json
import numpy as np
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import marshmallow as mm
from shapely import geometry
from AnnotationJsonSchema import AnnotationFile

def merge_bounding_box(box1,box2):
    if box1 is None:
        return box2
    if box2 is None:
        return box1
    
    outbox = {}
    for dim in ['X','Y','Z']:
        field = 'min'+dim
        outbox[field]=min(box1[field],box2[field])
        field = 'max'+dim
        outbox[field]=max(box1[field],box2[field])
    return outbox

def box_volume(box,voldim={'X':3,'Y':3,'Z':3}):
    vol = 1
    for dim in ['X','Y','Z']:
        vol*=voldim[dim]*(box['max'+dim]-box['min'+dim])
    return vol

def get_box_of_path(path):
    box = {}
    mins = np.min(path['orig_path'],axis=0)
    maxs = np.max(path['orig_path'],axis=0)
    #print mins,maxs
    box['minX']=mins[0]
    box['minY']=mins[1]
    box['maxX']=mins[0]
    box['maxY']=mins[1]
    box['minZ']=path['z']
    box['maxZ']=path['z']
    return box

class MakeTrakEM2QCFigures(ModuleParameters):
        annotationFile = InputFile(required=True,metadata={'description':'name of stack to with annotations'})
        outputDir = mm.fields.Str(required=True,metadata={'description':'name of the directory to save files'})

if __name__ == '__main__':

    parameters={
        "annotationFile":"/nas4/data/EM_annotation/annotationFilesForJHU/m247514_Site3Annotation_RD.json",
        "outputDir":"/nas4/data/EM_annotation/annotationFilesForJHU/m247514_Site3Annotation_RD_QCFigures"
    }


    mod = JsonModule(schema_type=MakeTrakEM2QCFigures,input_data = parameters)

    schema = AnnotationFile()
    with open(mod.args['annotationFile'],'r') as fp:
        json_raw = json.load(fp)
        result = schema.load(json_raw)
    print result.errors

    json_output = result.data
    print "loaded %d area lists"%len(json_output['area_lists'])

    area_lists = json_output['area_lists']
    #calculate the bounding boxes
    bboxes= []    
    volumes = np.zeros(len(area_lists))
    dzs = np.zeros(len(area_lists))
    overallbbox = None
    for i,al in enumerate(area_lists):
        bbox = None
        points = None
        
        for area in al['areas']:
            for path in area['paths']:
                p = path['orig_path']
                pathbox = get_box_of_path(path)
                bbox=merge_bounding_box(bbox,pathbox)
        
        bboxes.append(bbox)
        volumes[i]=box_volume(bbox)/(1000*1000*1000)
        dzs[i] = bbox['maxZ']-bbox['minZ']
        overallbbox=merge_bounding_box(overallbbox,bbox)


    subdir=mod.args['outputDir']
    if not os.path.isdir(subdir):
        os.makedirs(subdir)
    i=0
    zipup=zip(volumes,area_lists)
    order = zip(np.argsort(volumes),range(len(volumes)))

    from pathos.multiprocessing import Pool
    from functools import partial


    pool = Pool(30)


    def make_plot(area_lists,overallbbox,subdir,dzs,ki):
        (k,i) = ki
        al = area_lists[k]
        #if volumes[k]>.1:
        f,ax = plt.subplots(1,1,figsize=(14,14))
        #print bboxes[i]
       
        if dzs[k]>10:
            c='r-x'
        else:
            c='g-x'

        for area in al['areas']:
            for path in area['paths']:
                poly = geometry.Polygon(path['orig_path'])
                x,y = poly.boundary.xy
                #print poly
                ax.plot(np.array(x),np.array(y)*-1,c,)
        #print volumes[i]
        ax.set_title(al['oid']+' dz:%d'%dzs[k])
        ax.set_xlim([overallbbox['minX'],overallbbox['maxX']])
        ax.set_ylim([-overallbbox['maxY'],-overallbbox['minY']])
        f.savefig(os.path.join(subdir,'%07d.png'%i))
        
        f.clf()
        plt.close()


    mypartial = partial(make_plot,area_lists,overallbbox,subdir,dzs)
    results = pool.map(mypartial,order)
