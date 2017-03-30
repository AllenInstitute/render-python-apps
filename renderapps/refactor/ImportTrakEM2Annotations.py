import numpy as np
import json_module
import renderapi
import json
import numpy as np
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from renderapps.module.render_module import RenderTrakEM2Parameters, TrakEM2RenderModule
import marshmallow as mm
from shapely import geometry
import lxml.etree

parameters={
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":8080,
        "owner":"Forrest",
        "project":"M247514_Rorb_1",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    "EMstack":"ALIGNEM_reg2",
    "trakem2project":"/nas4/data/EM_annotation/annotationFilesForJHU/annotationTrakEMprojects_M247514_Rorb_1/m247514_Site3Annotation_cropedToMatch_MN.xml",
    "outputAnnotationFile":"/nas4/data/EM_annotation/annotationFilesForJHU/m247514_Site3Annotation_cropedToMatch_MN_local.json",
    "renderHome":"/pipeline/render"
}

parameters={
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":8080,
        "owner":"Forrest",
        "project":"M247514_Rorb_1",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    "EMstack":"ALIGNEM_reg2",
    "trakem2project":"/nas4/data/EM_annotation/annotationFilesForJHU/annotationTrakEMprojects_M247514_Rorb_1/m247514_Site3Annotation_cropedToMatch_SD.xml",
    "outputAnnotationFile":"/nas4/data/EM_annotation/annotationFilesForJHU/m247514_Site3Annotation_cropedToMatch_SD_local.json",
    "renderHome":"/pipeline/render"
}

parameters={
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":8080,
        "owner":"Forrest",
        "project":"M247514_Rorb_1",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    "EMstack":"ALIGNEM_reg2",
    "trakem2project":"/nas4/data/EM_annotation/annotationFilesForJHU/annotationTrakEMprojects_M247514_Rorb_1/m247514_Site3Annotation_RD.xml",
    "outputAnnotationFile":"/nas4/data/EM_annotation/annotationFilesForJHU/m247514_Site3Annotation_RD.json",
    "renderHome":"/pipeline/render"
}

class ImportTrakEM2Annotations(RenderTrakEM2Parameters):
    EMstack = mm.fields.Str(required=True,metadata={'description':'stack to look for trakem2 patches in'})
    trakem2project = json_module.InputFile(required=True,metadata={'description':'trakem2 file to read in'})
    outputAnnotationFile = mm.fields.Str(required=True,metadata={'description':'name of stack to save annotation tilespecs'})


def convert_path(path,tform):
    #function to convert TEM2 path using the transformation tform 
    #convert_path(path,tform):
    d = path.attrib['d'].split(' ')
    Nelem = int(np.ceil(len(d)*1.0/3))
    points = np.zeros((Nelem,2))
    
    for k,i in enumerate(range(0,len(d)+1,3)):

        if d[i]=='M':
            points[k,:]=[float(d[i+1]),float(d[i+2])]
        elif d[i]=='L':
            points[k,:]=[float(d[i+1]),float(d[i+2])]
        elif d[i]=='z':
            points[k,:]=points[0,:]
    return tform.tform(points)
            
def convert_transform(tfs):
    tfs=tfs.replace('matrix(','')
    tfs=tfs.replace(')','')
    vals = tfs.split(',')
    tform = renderapi.transform.AffineModel(M00 = vals[0],
                                           M10 = vals[1],
                                           M01 = vals[2],
                                           M11 = vals[3],
                                           B0  = vals[4],
                                           B1  = vals[5])
    return tform

def parse_area_lists(area_lists):
    json_output = {'area_lists':[]}
    for al in area_lists:
        areas = al.findall('t2_area')
        links=al.attrib['links']
        tform = convert_transform(al.attrib['transform'])
        area_list_d = dict(al.attrib)
        area_list_d['areas']=[]
        for area in areas:
            
            layerid=area.attrib['layer_id']
           
            area_d = dict(area.attrib)
            
            layer=root.find('//t2_layer[@oid="%s"]'%layerid)
            patches = [patch for patch in layer.getchildren()]
            patchids = [patch.attrib['oid'] for patch in patches]
            layer_tilespecs = [(poly,ts,t) for poly,ts,t in zip(tem2_polygons,tem2_tilespecs,render_tilespecs) if ts.tileId in patchids]
            
            paths = area.findall('t2_path')
            area_d['paths']=[]
            for path in paths:
                path_d = {}
                path_d['tile_paths']=[]
                path_numpy= convert_path(path,tform)            
                path_poly = geometry.Polygon(path_numpy)
                for poly,ts,rts in layer_tilespecs:
                    if poly.intersects(path_poly):
                        tile_path_d={}
                    
                        local_path = path_numpy
                        tmp=list(ts.tforms)
                        tmp.reverse()
                        for t in tmp:
                            local_path = t.inverse_tform(local_path)
                        tile_path_d['tileId']=rts.tileId
                        tile_path_d['z']=rts.z
                        #print 'z',rts.z,layerid,al.attrib['oid']
                        tile_path_d['path']=local_path
                path_d['tile_paths'].append(tile_path_d)

                path_d['z']=path_d['tile_paths'][0]['z']
                path_d['orig_path']=np.hstack((path_numpy,path_d['z']*np.ones((path_numpy.shape[0],1),np.float)))

                area_d['paths'].append(path_d)
               
            #for ts in linked_tilespecs:
            #    print ts.to_dict()
            area_list_d['areas'].append(area_d)
           
        json_output['area_lists'].append(area_list_d)
    return json_output
 
#function to convert a tilespec to a shapely polygon with its corners in global coordinates
def tilespec_to_bounding_box_polygon(ts):
    corners=np.array([[0,0],[0,ts.height],[ts.width,ts.height],[ts.width,0]])
    for tform in ts.tforms:
        corners=tform.tform(corners)
    return geometry.Polygon(corners) 


if __name__ == '__main__':

    mod = TrakEM2RenderModule(input_data = parameters,
                              schema_type = ImportTrakEM2Annotations)

    tem2file = mod.args['trakem2project']
    trakem2dir = os.path.split(tem2file)[0]
    jsonFileOut = os.path.join(trakem2dir,os.path.splitext(tem2file)[0]+'.json')

    #convert the trakem2 project to a json tilespec
    mod.convert_trakem2_project(tem2file,trakem2dir,jsonFileOut)

    #read in the tilespecs from the json, and parse them with api
    tsjson = json.load(open(jsonFileOut,'r'))
    tem2_tilespecs = [renderapi.tilespec.TileSpec(json=tsj) for tsj in tsjson]

    #loop over the tem2 tilespecs to find the corresponding render tilespecs
    # matching based upon the filename (due to moving of the data)

    render_tilespecs = []
    for ts in tem2_tilespecs:
        pot_render_tilespecs = mod.render.run(renderapi.tilespec.get_tile_specs_from_z,
                                             mod.args['EMstack'],
                                             ts.z)
        filepath = os.path.split(ts.ip.get(0)['imageUrl'])[1]
        pot_filepaths = [os.path.split(t.ip.get(0)['imageUrl'])[1] for t in pot_render_tilespecs]
        render_tilespecs.append(next(t for t,fp in zip(pot_render_tilespecs,pot_filepaths) if fp==filepath))
    #convert the tem2_tilespecs to shapely polygons
    tem2_polygons = [tilespec_to_bounding_box_polygon(ts) for ts in tem2_tilespecs]

    #parse the TEM2 project
    root = lxml.etree.parse(open(tem2file,'r'))

    #get the area lists
    area_lists=root.findall('//t2_area_list')
    area_lists = [al for al in area_lists if (len(al.getchildren())>0)]
    print 'project contains %d area lists'%len(area_lists)

    #parse the area lists into json
    json_output = parse_area_lists(area_lists)
    len(json_output['area_lists'])

    #dump the json dictionary through the AnnotationFile schema
    #in order to serialize it to disk
    from AnnotationJsonSchema import AnnotationFile
    schema = AnnotationFile()
    test = schema.dump(json_output)
    fp = open(mod.args['outputAnnotationFile'],'w')
    print test.errors
    json.dump(test.data,fp)
    fp.close()

# #calculate the bounding boxes
# bboxes= []    
# volumes = np.zeros(len(json_output['area_lists']))

# for i,al in enumerate(json_output['area_lists']):
#     bbox = None
#     points = None
    
#     for area in al['areas']:
#         for path in area['paths']:
#             p = path['orig_path']
#             pathbox = get_box_of_path(path)
#             bbox=merge_bounding_box(bbox,pathbox)
    
#     bboxes.append(bbox)
#     volumes[i]=box_volume(bbox)/(1000*1000*1000)


# # In[40]:



# # In[228]:

# f,ax = plt.subplots(1,1)
# ans=ax.hist(volumes,bins=np.arange(0,.1,.001))


# # In[41]:



# subdir=os.path.splitext(os.path.split(mod.args['trakem2project'])[1])[0]
# if not os.path.isdir(subdir):
#     os.makedirs(subdir)
# i=0
# zipup=zip(volumes,json_output['area_lists'])
# order = np.argsort(volumes)

# for k in order:
#     al = json_output['area_lists'][k]
#     #if volumes[k]>.1:
#     f,ax = plt.subplots(1,1,figsize=(14,14))
#     #print bboxes[i]
#     c = np.random.rand(3,1)
#     for area in al['areas']:
#         for path in area['paths']:
#             poly = geometry.Polygon(path['orig_path'])
#             x,y = poly.boundary.xy
#             #print poly
#             ax.plot(np.array(x),np.array(y)*-1,'r')
#     #print volumes[i]
#     ax.set_title(al['oid'])
#     ax.set_xlim([-2600,2700])
#     ax.set_ylim([-3000,1540])
#     f.savefig(os.path.join(subdir,'%07d.png'%i))
#     i+=1


# # In[31]:

# np.sort()


# # In[159]:

# np.array(x)


# # In[150]:

# al['oid']


# # In[107]:

# print volumes[volumes>1]
# print np.sum(volumes>1)*1.0/len(volumes)


# # In[108]:

# np.max(volumes)


# # In[95]:

# print volumes[volumes>1]
# print np.sum(volumes>1)*1.0/len(volumes)


# # In[ ]:




# # In[71]:




# # In[28]:




# # In[14]:

# print ts.ip.get(0)
# print ts.z
# render_tspecs=mod.render.run(renderapi.tilespec.get_tile_specs_from_z,
#                              mod.args['EMstack'],
#                              ts.z)


# # In[18]:

# for ts in render_tspecs:
#     print ts.ip.get(0)


# # In[11]:

# import matplotlib.pyplot as plt
# plt.plot(local_path[:,0],local_path[:,1])


# # In[17]:

# a=['a','b','c']
# b=list(a)
# a.reverse()
# print a
# print b


# # In[7]:

# 'ERROR' in 'ERROR IS HERE'


# # In[74]:

# renderapi.tilespec.AffineModel.tform()


# # In[12]:

# tform


# # In[34]:

# p2, Nd = tform.convert_to_point_vector(path)
# pt = np.dot(np.linalg.inv(tile_tform.M), p2.T).T
# print tform.convert_points_vector_to_array(pt, Nd)


# # In[31]:

# Nd


# # In[107]:

# import tempfile


# # In[110]:




# # In[ ]:



