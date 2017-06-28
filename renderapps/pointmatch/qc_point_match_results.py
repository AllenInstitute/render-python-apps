import renderapi
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from functools import partial
import pathos.multiprocessing as mp
from matplotlib.patches import FancyArrowPatch, Circle, ConnectionStyle
import os
from ..module.render_module import RenderModule, RenderParameters
from json_module import InputFile,InputDir
import marshmallow as mm
import json
import networkx as nx


example_parameters={
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":80,
        "owner":"S3_Run1",
        "project":"S3_Run1_Jarvis",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    "matchcollections":['S3_Run1_Jarvis_68_to_112_DAPI_1_highres_R1'],
    "input_tilepairfile":"/nas4/data/S3_Run1_Jarvis/processed/tilepairfiles1/tilepairs-10-145-165-nostitch-EDIT.json",
    "output_tilepairfile":"/nas4/data/S3_Run1_Jarvis/processed/tilepairfiles1/tilepairs-10-145-165-nostitch-QC.json",
    "figdir":"/nas3/data/S3_Run1_Jarvis/processed/matchfigures",
    "min_matches":5
}

example_parameters={
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":80,
        "owner":"S3_Run1",
        "project":"S3_Run1_Jarvis",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    "matchcollections":['S3_Run1_Jarvis_68_to_112_DAPI_1_highres_R1'],
    "input_tilepairfile":"/nas4/data/S3_Run1_Jarvis/processed/tilepairfiles1/tilepairs-10-170-200-nostitch-EDIT.json",
    "output_tilepairfile":"/nas4/data/S3_Run1_Jarvis/processed/tilepairfiles1/tilepairs-10-170-200-nostitch-QC.json",
    "figdir":"/nas3/data/S3_Run1_Jarvis/processed/matchfigures",
    "min_matches":5
}
#example_parameters={
#    "render":{
#        "host":"ibs-forrestc-ux1",
#        "port":80,
#        "owner":"S3_Run1",
#        "project":"S3_Run1_Jarvis",
#        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
#    },
#    "matchcollections":['S3_Run1_Jarvis_68_to_112_DAPI_1_highres_R1'],
#    "input_tilepairfile":"/nas4/data/S3_Run1_Jarvis/processed/tilepairfiles1/tilepairs-10-300-400-nostitch-EDIT.json",
#    "output_tilepairfile":"/nas4/data/S3_Run1_Jarvis/processed/tilepairfiles1/tilepairs-10-300-400-nostitch-QC.json",
#    "figdir":"/nas3/data/S3_Run1_Jarvis/processed/matchfigures",
#    "min_matches":5
#}
example_parameters={
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":80,
        "owner":"S3_Run1",
        "project":"S3_Run1_Jarvis",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    "matchcollections":['S3_Run1_Jarvis_68_to_112_DAPI_1_highres_R1'],
    "input_tilepairfile":"/nas4/data/S3_Run1_Jarvis/processed/tilepairfiles1/tilepairs-10-655-694-nostitch-EDIT.json",
    "output_tilepairfile":"/nas4/data/S3_Run1_Jarvis/processed/tilepairfiles1/tilepairs-10-655-694-nostitch-QC.json",
    "figdir":"/nas3/data/S3_Run1_Jarvis/processed/matchfigures",
    "min_matches":5
}
example_parameters={
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":80,
        "owner":"S3_Run1",
        "project":"S3_Run1_Jarvis",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    "matchcollections":['S3_Run1_Jarvis_68_to_112_DAPI_1_highres_R1'],
    "input_tilepairfile":"/nas4/data/S3_Run1_Jarvis/processed/tilepairfiles1/tilepairs-10-145-165-nostitch-EDIT.json",
    "output_tilepairfile":"/nas4/data/S3_Run1_Jarvis/processed/tilepairfiles1/tilepairs-10-145-165-nostitch-QC.json",
    "figdir":"/nas3/data/S3_Run1_Jarvis/processed/matchfigures",
    "min_matches":5
}
class QCPointMatchResultsParameters(RenderParameters):
    matchcollections = mm.fields.List(mm.fields.Str,required=True,
        metadata={'description':'list of match collections to analyze'})
    input_tilepairfile = InputFile(required=True, 
        metadata = {'description':'file path of tile pair file to qc'})
    output_tilepairfile = mm.fields.Str(required=True,
        metadata = {'description':'file path of where to save the tile pair file to qc'})
    figdir = mm.fields.Str(required=True,
        metadata={'description':'directory to save images'})
    min_matches = mm.fields.Int(required=False,default=5,
        metadata={'description':'number of matches between tiles to be considered a valid match'})
    pool_size = mm.fields.Int(required=False,default=20,
        metadata={'description':'number of parallel threads to use'})

def make_plot(r,matchcollection,zvalues,figdir,item):
    section_p,section_q = item
    z_p = zvalues[section_p]
    z_q = zvalues[section_q]
    bounds_p = self.render.run(renderapi.stack.get_bounds_from_z,stack,z_p)
    #bounds_q = render.get_bounds_from_z(stack,z_q)
    allmatches = self.render.run(renderapi.pointmatch.get_matches_from_group_to_group,matchcollection,section_p,section_q)
    all_points_global_p = np.zeros((1,2))
    all_points_global_q = np.zeros((1,2))
    for matchobj in allmatches:
        points_local_p = np.array(matchobj['matches']['p'])
        points_local_q = np.array(matchobj['matches']['q'])

        t_p = self.render.run(renderapi.coordinate.local_to_world_coordinates_array,stack,points_local_p.T,matchobj['pId'],z_p)
        all_points_global_p=np.append(all_points_global_p,t_p,axis=0)

        t_q = self.render.run(renderapi.coordinate.local_to_world_coordinates_array,stack,points_local_q.T,matchobj['qId'],z_q)
        all_points_global_q=np.append(all_points_global_q,t_q,axis=0)

        #break
    all_points_global_p = all_points_global_p[1:,:]
    all_points_global_q = all_points_global_q[1:,:]
    all_points=np.concatenate([all_points_global_p,all_points_global_q],axis=1)
    width = bounds_p['maxX']-bounds_p['minX']
    height = bounds_p['maxY']-bounds_p['minY']
    wh_ratio = width*1.0/height
    if wh_ratio>1.0:
        f,ax=plt.subplots(1,1,figsize=(10,10/wh_ratio))
    else:
        f,ax=plt.subplots(1,1,figsize=(10*wh_ratio,10))

    #ax.imshow(lowmag_rg,extent=(bounds_p['minX'],bounds_p['maxX'],bounds_p['maxY'],bounds_p['minY']))
    ax.scatter(all_points[:,0],all_points[:,1],c='m',marker='o',s=5,linewidth=0)
    ax.quiver(all_points[:,0].T,all_points[:,1].T,
            all_points[:,2].T-all_points[:,0].T,
            all_points[:,3].T-all_points[:,1].T,
            color='m',
            angles='xy', scale_units='xy', scale=1)
    ax.set_xlim((bounds_p['minX'],bounds_p['maxX']))
    ax.set_ylim((bounds_p['maxY'],bounds_p['minY']))
    ax.set_aspect('equal')
    ax.set_title('%d_to_%d'%(z_p,z_q))
    #ax.autoscale(tight=True)
    plt.tight_layout()

    figpath = os.path.join(figdir,'%05d_to_%05d.png'%(z_p,z_q))

    f.savefig(figpath)
    plt.close(f)
    return figpath

def check_pair(render,matchcollections,pair):
    matches = []
    for matchcollection in matchcollections:
        matches+=renderapi.pointmatch.get_matches_from_tile_to_tile(matchcollection,
            pair['p']['groupId'],
            pair['p']['id'],
            pair['q']['groupId'],
            pair['q']['id'],
            render=render)
    if len(matches)>0:
        return len(matches[0]['matches']['p'][0])
    else:
        return 0

def get_bad_pairs(render,tilepairjson,matchcollections,min_matches,pool_size=20):
    
    stack= tilepairjson['renderParametersUrlTemplate'].split('/')[6]

    zvals = np.array(render.run(renderapi.stack.get_z_values_for_stack,stack))

    with renderapi.client.WithPool(pool_size) as pool:
        match_numbers=pool.map(partial(check_pair,render,matchcollections),tilepairjson['neighborPairs'])
    match_numbers = np.array(match_numbers)
    badones= np.where(match_numbers<min_matches)[0]
    badpairs= np.array(tilepairjson['neighborPairs'])[badones]
    bad_tilepairjson = {
        'renderParametersUrlTemplate':tilepairjson['renderParametersUrlTemplate'],
        'neighborPairs':badpairs.tolist()
    }
    return bad_tilepairjson,match_numbers

def add_pair_to_graph(G,sectionId):
    if not G.has_node(sectionId):
        G.add_node(sectionId)

def compare_graph(G,sg1,sg2):
    z1 = np.min(np.array([G.node[node]['z'] for node in sg1]))
    z2 = np.min(np.array([G.node[node]['z'] for node in sg2]))
    return int(z1-z2)


def define_connected_components_by_section(render,tilepairjson,match_numbers,min_matches=5,pool_size=20):
    stack= tilepairjson['renderParametersUrlTemplate'].split('/')[6]
    G=nx.Graph()

    for i,pair in enumerate(tilepairjson['neighborPairs']):
        section_p = int(pair['p']['groupId'])
        section_q = int(pair['q']['groupId'])
        add_pair_to_graph(G,section_p)
        add_pair_to_graph(G,section_q)
        if match_numbers[i]>min_matches:
            if G.has_edge(section_p,section_q):
                w = G[section_p][section_q]['weight']
                G[section_p][section_q]['weight']=w+match_numbers[i]
            else:
                G.add_edge(section_p,section_q,weight=match_numbers[i])

    zvalues = {}
    with renderapi.client.WithPool(pool_size) as pool:
        mypartial = partial(renderapi.stack.get_z_value_for_section,stack,render=render)
        zs = pool.map(mypartial,G.nodes())
    for node,z in zip(G.nodes(),zs):
        zvalues[node]=z
        G.node[int(node)]['z']=z
    subgraphs=nx.connected_components(G)
    subgraphs = [sg for sg in subgraphs]
    subgraphs.sort(partial(compare_graph,G))
    #f,ax = plt.subplots(figsize=(8,6))
    for i,sG in enumerate(subgraphs):
        zs = np.array([G.node[node]['z'] for node in sG])
        print np.min(zs),'-',np.max(zs)
    
class QCPointMatchResults(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = QCPointMatchResultsParameters
        super(QCPointMatchResults,self).__init__(schema_type=schema_type,*args,**kwargs)

    def run(self):
        with open(self.args['input_tilepairfile'],'r') as fp:
            tilepairjson = json.load(fp)
    
        bad_tilepairjson,match_numbers = get_bad_pairs(self.render,
            tilepairjson,
            self.args['matchcollections'],
            self.args['min_matches'],
            self.args['pool_size'])

        define_connected_components_by_section(self.render,
            tilepairjson,
            match_numbers,
            pool_size = self.args['pool_size'])

        with open(self.args['output_tilepairfile'],'w') as fp:
            json.dump(bad_tilepairjson,fp)

        #figdir='%s-%s-%s'%(self.args['figdir'],self.args['matchcollection'],stack)
        #if not os.path.isdir(figdir):
        #     os.makedirs(figdir)

 
        
if __name__ == "__main__":
    mod = QCPointMatchResults(input_data = example_parameters)
    mod.run()

