import os
from functools import partial
from argschema import ArgSchema, ArgSchemaParser
import argschema
import marshmallow as mm
from renderapps.TrakEM2.AnnotationJsonSchema import AnnotationFile, NumpyArray
import json
import pandas as pd
from rtree import index
from shapely import geometry
import numpy as np
import pprint as pp
#import pdb
example_json = {
    "EM_annotation_json":"/nas3/data/M247514_Rorb_1/annotation/m247514_Site3Annotation_MN_global_v2.json",
    "LM_annotation_json":"/nas3/data/M247514_Rorb_1/processed/Site3AlignStacks/glut_synapses46a_global.json",
    "EM_boundary_json":"/nas3/data/M247514_Rorb_1/annotation/m247514_Site3Annotation_MN_bb_Site3Align2_global.json",
    "EM_metadata_csv":"https://docs.google.com/spreadsheets/d/1cV6BuQosLgjZX1e2l9EZHTOSLZGlDETKjlv2-wjpeIk/export?gid=607779864&format=csv",
    "EM_inclass_column1":"GABA",
    "EM_inclass_column2":"tdTom",
    "EM_inclass_invert":False,
    "EM_inclass_conditions1":[1],
    "EM_inclass_conditions2":[2,3],
    "EM_not_synapse_column":"NotSynapse",
    "output_json":"/nas3/data/M247514_Rorb_1/processed/Site3AlignStacks/glut_synapses45a_evaluation.json"
    }
# example_json = {
#     "EM_annotation_json":"/nas3/data/M247514_Rorb_1/annotation/m247514_Take2Site4Annotation_MN_Take2Site4global.json",
#     "LM_annotation_json":"/nas3/data/M247514_Rorb_1/processed/Take2Site4AlignStacks/glut_synapses15a_global.json",
#     "EM_metadata_csv":"https://docs.google.com/spreadsheets/d/1zp3mApWRo5xyg1tqOSt7Ddp0LC7xWIFaFbsxZrk73bQ/export?gid=0&format=csv",
#     "EM_inclass_column":"GABA",
#     "EM_inclass_invert":True,
#     "EM_not_synapse_column":"NotSynapse",
#     "output_json":"/nas3/data/M247514_Rorb_1/processed/Take2Site4AlignStacks/glut_synapses15a_evaluation.json"
#     }


class EvaluateSynapseDetectionParameters(ArgSchema):
    EM_annotation_json = argschema.fields.InputFile(required=True,
        description='file path to EM annotation file')
    LM_annotation_json = argschema.fields.InputFile(required=True,
        description='file path to LM annotation results') 
    EM_boundary_json = argschema.fields.InputFile(required=True,
        description='file path to boundary area list')
    EM_metadata_csv = argschema.fields.Url(required=True,
        description='file path to EM metadata csv')
    EM_inclass_column1 = argschema.fields.Str(required=True,
        description="name of column in metadata that indicates whether synapse is gabaergic") 
    EM_inclass_column2 = argschema.fields.Str(required=True,
        description="name of column in metadata that indicates whether synapse is gabaergic") 
    EM_inclass_conditions1=argschema.fields.NumpyArray(required=False,default=[1],
                                                      description="what values of EM_inclass_column are considered in class")
    EM_inclass_conditions2=argschema.fields.NumpyArray(required=False,default=[1],
                                                      description="what values of EM_inclass_column are considered in class")
    EM_inclass_invert = argschema.fields.Boolean(required=False,default=False,description="whether to invert the class columns")
    EM_not_synapse_column = argschema.fields.Str(required=True,
        description="name of column that indicates whether this annotation should be ignored")
    edge_distance = argschema.fields.Int(required=False, default = 100,
        description="""distance from the edge of the bounding box in world coordinates
        (same as global_path units) for annotation to be considered edge""")
    edge_min_sections = argschema.fields.Int(required=False,default=4,
        description="synapses occuring in fewer than this many sections and bordering the first or last section will be considered to be edge cases")

class EvaluateSynapseDetectionOutput(mm.Schema):
    LM_per_EM = argschema.fields.NumpyArray(dtype=np.float,required=True,
        description="list of fraction of EM synapses with 0,1, or 2+ synapses over them")
    EM_per_LM = argschema.fields.NumpyArray(dtype=np.float,required=True,
        description ="list of fraction of LM synapses with 0,1, or 2+ EM synapses over them")
    missed_EM = argschema.fields.List(argschema.fields.Str, required=True,
        description= "list of EM synapses oids for which there were no LM detections")
    split_EM = argschema.fields.List(argschema.fields.Str, required=True,
        description= "list of EM synapses oids for which there were LM detections")
    correct_EM = argschema.fields.List(argschema.fields.Str, required=True,
        description= "list of EM synapses oids for which there were exactly one LM detections")
    false_pos_LM = argschema.fields.List(argschema.fields.Str, required=True,
        description= "list of LM synapses oids for which there were no EM synapses")
    merge_LM = argschema.fields.List(argschema.fields.Str, required=True,
        description= "list of LM synapses oids for which there were more than one EM synapses")
    correct_LM = argschema.fields.List(argschema.fields.Str, required=True,
        description= "list of LM synapses oids for which there were more exactly one EM synapses")

def load_annotation_file(annotation_path):
    """function to read an annotation file from disk

    Parameters
    ----------
    annotation_path: str
        path to annotation file on disk
    
    Returns
    -------
    list[dict]:
        A list of dictionaries following the AnnotationFile schema that contains the annotations
    """
    with open(annotation_path,'r') as fp:
            annotation_d = json.load(fp)
    schema = AnnotationFile()
    annotations,errors = schema.load(annotation_d)      
    if len(errors)>0:
        print(errors)
    assert(len(errors)==0)
    return annotations["area_lists"]

def get_bounding_box_of_al(al):
    """a function to return a bounding box of an annotation

    Parameters
    ----------
    al: dict
        an arealist following the AreaList schema in AnnotationFile

    Returns:
    tuple:
        (minX,minY,minZ,maxX,maxY,maxZ) tuple of bounding box
    """
    Nareas = len(al['areas'])
    mins = np.zeros((Nareas,2))
    maxs = np.zeros((Nareas,2))
    zvalues = []
    for i,area in enumerate(al['areas']): 
        gp = area['global_path']
        mins[i,:] = np.min(gp,axis=0)
        maxs[i,:] = np.max(gp,axis=0)
        zvalues.append(area['z'])
    gmin = np.min(mins,axis=0)
    gmax = np.max(maxs,axis=0)
    minX = gmin[0]
    minY = gmin[1]
    maxX = gmax[0]
    maxY = gmax[1]
    minZ = np.min(zvalues)
    maxZ = np.max(zvalues)
    return (minX,minY,minZ,maxX,maxY,maxZ)

def get_annotation_bounds_df(annotations):
    """function to get a pandas dataframe of annotation bounds from a list of annotations

    Parameters
    ----------
    annotations: list[dict]
        a list of annotation dictionaries that follow to the AreaList schema
    
    Returns
    -------
    pandas.DataFrame:
        A data frame containing the following columns 'oid','minX','minY','minZ','maxX','maxY','maxZ'
    """ 
    ds=[]
    for al in annotations:
        (minX,minY,minZ,maxX,maxY,maxZ)=get_bounding_box_of_al(al)
        ds.append({
            'oid':al['oid'],
            'minX':minX,
            'minY':minY,
            'minZ':minZ,
            'maxX':maxX,
            'maxY':maxY,
            'maxZ':maxZ,
        })
    df = pd.DataFrame(ds)
    return df

def get_bounding_box_of_annotations(annotations):
    """a function to get the overall bounding box surrounding all the annotations
   
    Parameters
    ----------
    annotations: list[dict]
        a list of annotation dictionaries that follow to the AreaList schema
    
    Returns:
    tuple:
        (minX,minY,minZ,maxX,maxY,maxZ) tuple of bounding box that contains all annotations
    """
    df = get_annotation_bounds_df(annotations)
    ann_minX=df.min().minX
    ann_minY=df.min().minY
    ann_maxX=df.max().maxX
    ann_maxY=df.max().maxY
    ann_minZ=df.min().minZ
    ann_maxZ=df.max().maxZ
    return (ann_minX,ann_minY,ann_minZ,ann_maxX,ann_maxY,ann_maxZ)

def is_annotation_near_edge(al,EM_boundaries,
                            distance=100,min_edge_sections=4):
    """function to test if annotation is near the 'edge' of a dataset

    Parameters
    ----------
    al: dict
        annotation dictionary
    EM_boundaries: dict
        em boundary dictionary
    distance: int
        x,y distance from edge to be considered near edge (default 100)
    min_edge_section: int
        if annotation is in fewer than these number of sections
        and touches z border of dataset it will be considered in edge (default 4)
    
    Returns
    -------
    bool:
        True/False if this annotation is near edge
    """
    
    ann_boundary_zs = np.array([alb['areas'][0]['z'] for alb in EM_boundaries])
    ann_minZ = np.min(ann_boundary_zs)
    ann_maxZ = np.max(ann_boundary_zs)
    zvals=np.unique(np.array([area['z'] for area in al['areas']]))
    if len(zvals)<min_edge_sections:
        if ann_minZ in zvals:
            #print('min z fail',zvals)
            return True
        if ann_maxZ in zvals:
            #print('max z fail',zvals)
            return True
    if np.max(zvals)<ann_minZ:
        #print('out z min fail',zvals)
        return True
    if np.min(zvals)>ann_maxZ:
        #print('out z max fail',zvals)
        return True
    
    #pdb.set_trace()
    for area in al['areas']:
        try:
            boundary_area = next(alb['areas'][0] for alb in EM_boundaries if alb['areas'][0]['z']==area['z'])
            has_boundary =True
        except:
            has_boundary = False
        if has_boundary:
            boundary = geometry.Polygon(boundary_area['global_path'])
            b2 = boundary.buffer(-distance)
            poly1 = geometry.Polygon(area['global_path'])
            try:
                if(not b2.contains(poly1)):
                    #print('area failed',area['global_path'],boundary_area['global_path'])
                    return True
            except:
                print(area['global_path'])
                assert False          

        
    #print('pass',al['oid'])
    return False

def get_edge_annotations(annotations,EM_boundaries,
                         distance=100,
                         min_edge_sections=4):
    """function to get list of True/False values of whether annotation is near the 'edge' of a dataset

    Parameters
    ----------
    annotations: dict
        annotation dictionary
    EM_boundaries: dict
        em boundary dictionary
    distance: int
        x,y distance from edge to be considered near edge (default 100)
    min_edge_section: int
        if annotation is in fewer than these number of sections
        and touches z border of dataset it will be considered in edge (default 4)
    
    Returns
    -------
    list[bool]:
        list of True/False if annotations are near edge
    """
    is_edge = np.zeros(len(annotations),np.bool)
    for k,al in enumerate(annotations):
        is_edge[k]=is_annotation_near_edge(al,
                                        EM_boundaries,
                                        distance=distance,
                                        min_edge_sections=min_edge_sections)
    return is_edge


def get_index(name='LM_index'):
    """function to get a spatial index, removing existing one if it exists

    Parameters
    ----------
    name: str
        name of index

    Returns
    -------
    rtree.Index:
        new index ready to be filled
    """

    dataname = '{}.dat'.format(name)
    indexname = '{}.idx'.format(name)
    if os.path.isfile(dataname):
        os.remove(dataname)
    if os.path.isfile(indexname):
        os.remove(indexname) 
    p = index.Property()
    p.dimension=3
    return index.Index(name,properties = p)

def insert_annotations_into_index(index,annotations):
    """function to insert annotations into rtree index

    Parameters
    ----------
    index: rtree.index
        spatial index to insert
    annotations: list[dict]
        list of annotations following area_list schema in AnnotationFile schema

    Returns
    -------
    list:
        a list of (minX,minY,minZ,maxX,maxY,maxZ) tuples containing bounds of annotations
    """

    bound_list=[]
    for i,al in enumerate(annotations):
        bounds = get_bounding_box_of_al(al)
        bound_list.append(bounds)
        index.insert(i,bounds)
    return bound_list

def do_annotations_overlap(al1,al2):
    """function to test of two annotations overlap

    Parameters
    ----------
    al1: dict
        AreaList dictionary that follows schema in AnnotationJsonSchema.AnnotationFile
    al2: dict
        AreaList dictionary that follows schema in AnnotationJsonSchema.AnnotationFile
    
    Returns
    -------
    bool:
        True/False whether they overlap
    """

    for area2 in al2['areas']:
        poly2 = geometry.Polygon(area2['global_path'])
        for area1 in al1['areas']:
            if int(area1['z'])==int(area2['z']):
                poly1 = geometry.Polygon(area1['global_path'])
                if poly1.intersects(poly2):
                    return True,area1['z']
    return False,None

def annotations_to_df(annotations):
    dl = []
    for al in annotations:
        for a in al['areas']:
            a.update({'oid':al['oid'],'id':al['id']}) 
            mins=np.min(a['global_path'],axis=0)
            maxs=np.max(a['global_path'],axis=0)
            a['minX']=mins[0]
            a['minY']=mins[1]
            a['maxX']=maxs[0]
            a['maxY']=maxs[1]
            dl.append(a)
    return pd.DataFrame(dl)

def get_overlap_matrix(good_annotations, LM_annotations, EM_index, LM_bounds):
    overlap_matrix = np.zeros((len(good_annotations),len(LM_annotations)),np.bool)
    j=0
    for i,alLM in enumerate(LM_annotations):
        res=EM_index.intersection(LM_bounds[i])
        for k in res:
            alEM=good_annotations[k]
            overlaps,zsection = do_annotations_overlap(alLM,alEM)
            if overlaps:
                overlap_matrix[k,i]=True
    return overlap_matrix

class EvaluateSynapseDetection(ArgSchemaParser):
    """Module for evaluating synapse detection results given EM ground truth"""
    default_schema = EvaluateSynapseDetectionParameters
    default_output_schema = EvaluateSynapseDetectionOutput

    def run(self):
        pp.pprint(self.args)
        EM_annotations = load_annotation_file(self.args['EM_annotation_json'])
        LM_annotations = load_annotation_file(self.args['LM_annotation_json'])
        df = pd.read_csv(self.args['EM_metadata_csv'], index_col=0,skiprows=1,dtype={'oid':np.object})
        good_rows = (~(np.uint8(df[self.args['EM_not_synapse_column']])>0.0))
        in_class_rows1 = np.isin(df[self.args['EM_inclass_column1']],self.args['EM_inclass_conditions1'])
        in_class_rows2 = np.isin(df[self.args['EM_inclass_column2']],self.args['EM_inclass_conditions2'])
        
        #if self.args['EM_inclass_invert']:
        #    in_class_rows = ~in_class_rows
        good_rows = good_rows & in_class_rows1 & in_class_rows2  
        good_df=df[good_rows]
        good_annotations = [al for al in EM_annotations if np.sum(good_df.oid.str.match(al['oid']))>0] 
    
        EM_boundaries = load_annotation_file(self.args['EM_boundary_json'])
        
        #(ann_minX,ann_minY,ann_minZ,ann_maxX,ann_maxY,ann_maxZ) = get_bounding_box_of_annotations(good_annotations)

        print("number of good rows",good_df.shape)

        print("len of good_annotations",len(good_annotations))
        
        EM_edge=get_edge_annotations(good_annotations,EM_boundaries,
                    distance=self.args['edge_distance'],
                    min_edge_sections=self.args['edge_min_sections'])
        
        LM_edge=get_edge_annotations(LM_annotations,EM_boundaries,
                         distance=self.args['edge_distance'],
                         min_edge_sections=self.args['edge_min_sections'])

        LM_index=get_index('LM_index')
        LM_bounds=insert_annotations_into_index(LM_index,LM_annotations)
        EM_index = get_index('EM_index')
        EM_bounds=insert_annotations_into_index(EM_index,good_annotations)

        overlap_matrix = get_overlap_matrix(good_annotations, LM_annotations, EM_index, LM_bounds)
        
        bins = np.arange(0,4)
        LM_per_EM = np.sum(overlap_matrix,axis=1)
        EM_per_LM = np.sum(overlap_matrix,axis=0)
        LM_per_EM_counts,edges = np.histogram(LM_per_EM[EM_edge==False],bins=bins,normed=True)
        EM_per_LM_counts,edges = np.histogram(EM_per_LM[LM_edge==False],bins=bins,normed=True)
        print("EM_per_LM",EM_per_LM_counts)
        print("LM_per_EM",LM_per_EM_counts)
        print('lm edge detections:',np.sum(LM_edge))
        print('em edge annotations',np.sum(EM_edge))
        print('LM detections:',len(LM_edge))
        d= {}
        d['EM_per_LM']=EM_per_LM_counts
        d['LM_per_EM']=LM_per_EM_counts
        d['missed_EM']= [al['oid'] for k,al in enumerate(good_annotations) if (EM_edge[k]==False) and (LM_per_EM[k]==0)]
        d['split_EM']= [al['oid'] for k,al in enumerate(good_annotations) if (EM_edge[k]==False) and (LM_per_EM[k]>1)]
        d['correct_EM']= [al['oid'] for k,al in enumerate(good_annotations) if (EM_edge[k]==False) and (LM_per_EM[k]==1)]
        d['false_pos_LM']= [al['oid'] for k,al in enumerate(LM_annotations) if (LM_edge[k]==False) and (EM_per_LM[k]==0)]
        d['merge_LM']= [al['oid'] for k,al in enumerate(LM_annotations) if (LM_edge[k]==False) and (EM_per_LM[k]>1)]
        d['correct_LM']= [al['oid'] for k,al in enumerate(LM_annotations) if (LM_edge[k]==False) and (EM_per_LM[k]==1)]
        print ('missed EM: ', d['missed_EM'])
        self.output(d)



if __name__ == '__main__':
    mod = EvaluateSynapseDetection(input_data= example_json)
    mod.run()
