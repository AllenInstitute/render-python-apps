import renderapi
from ..module.render_module import RenderModule, RenderParameters
import os
import json
import numpy as np
from rtree import index as rindex
import networkx as nx
import pathos.multiprocessing as mp
from functools import partial
from ..module.render_module import RenderModule, RenderParameters
import marshmallow as mm


example_json={
        "render":{
            "host":"ibs-forrestc-ux1",
            "port":8080,
            "owner":"Forrest",
            "project":"M247514_Rorb_1",
            "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
        },
        "prestitchedStack":"my example parameters",
        "poststitchedStack":"poststack",
        "outputStack":"name of output stack",
        "jsonDirectory":"directory to save",
        "edge_threshold":1843, #default
        "pool_size":20, #default
        "distance_threshold":50, #default

}

class DetectAndDropStitchingMistakesParameters(RenderParameters):
    prestitchedStack = mm.fields.Str(required=True,
        metadata={'description':'name of render stack of tiles before stitching'})
    poststitchedStack = mm.fields.Str(required=True,
        metadata={'description':'name of render stack of tiles after stitching'})
    outputStack = mm.fields.Str(required=True,
        metadata={'description':'name of render stack to output with stitching fixed'})
    jsonDirectory = mm.fields.Str(required=True,
        metadata={'description:':'directory to save json files'})
    edge_threshold  = mm.fields.Int(required=False,default=1843,
        metadata={'description:':'distance between tilespecs to consider as edges(default=1843)'})
    pool_size  = mm.fields.Int(required=False,default=20,
        metadata={'description:':'degree of parallelism (default=20)'})
    distance_threshold  = mm.fields.Int(required=False,default=50,
        metadata={'description:':'amplitude difference between pre and post stitching results,\
         that causes edge to be tossed (units of render)(default=50)'})
    


def process_section(z,
    render=None,
    prestitchedStack='',
    poststitchedStack='',
    outputStack='',
    distance_threshold=50,
    edge_threshold=1843):

    ridx = rindex.Index() #setup an Rtree to find overlapping tiles
    G=nx.Graph() #setup a graph to store overlapping tiles
    Gpos = {} #dictionary to store positions of tiles
    
    #get all the tilespecs for this z from prestitched stack
    pre_tilespecs = renderapi.tilespec.get_tile_specs_from_z(prestitchedStack, z, render=renderapi)
    #insert them into the Rtree with their bounding boxes to assist in finding overlaps
    #label them by order in pre_tilespecs
    [ridx.insert(i,(ts.minX,ts.minY,ts.maxX,ts.maxY)) for i,ts in enumerate(pre_tilespecs)]
    
    post_tilespecs = []
    #loop over each tile in this z to make graph
    for i,ts in enumerate(pre_tilespecs):
        #create the list of corresponding post stitched tilespecs
        post_tilespecs.append(renderapi.tilespec.get_tile_spec(poststitchedStack,ts.tileId,render=render))
        
        #get the list of overlapping nodes
        nodes=list(ridx.intersection((ts.minX,ts.minY,ts.maxX,ts.maxY)))
        nodes.remove(i) #remove itself
        [G.add_edge(i,node) for node in nodes] #add these nodes to the undirected graph
        
        #save the tiles position
        Gpos[i]=((ts.minX+ts.maxX)/2,(ts.minY+ts.maxY)/2)
        
    #loop over edges in the graph
    for p,q in G.edges():
        #p and q are now indices into the tilespecs, and labels on the graph nodes
        
        #assuming the first transform is the right one, and is only translation
        #this is the vector between these two tilespecs
        dpre=pre_tilespecs[p].tforms[0].M[0:2,3]-pre_tilespecs[q].tforms[0].M[0:2,3]
        #this is therefore the distance between them
        dp = np.sqrt(np.sum(dpre**2))
        #this is the vector between them after stitching
        dpost=post_tilespecs[p].tforms[0].M[0:2,3]-post_tilespecs[q].tforms[0].M[0:2,3]
        #this is the amplitude of the vector between the pre and post vectors (delta delta vector)
        delt = np.sqrt(np.sum((dpre-dpost)**2))
        #store it in the edge property dictionary
        G[p][q]['distance']=delt
        #if the initial distance was too big, or if the delta delta vector is too large
        if (delt>distance_threshold) | (dp>edge_threshold):
            #remove the edge
            G.remove_edge(p,q)

    #after removing all the bad edges...
    #get the largest connected component of G
    Gc = max(nx.connected_component_subgraphs(G), key=len)
    
    #use it to pick out the good post stitch tilspecs that remain in the graph
    ts_good_json = [post_tilespecs[node].to_dict() for node in Gc.nodes_iter()]
    #formulate a place to save them
    jsonfilepath = os.path.join(a.jsonDirectory,'%s_z%04.0f.json'%(outputStack,z))
    #dump the json to that location
    json.dump(ts_good_json,open(jsonfilepath ,'w'))
    #return the name of the file
    return jsonfilepath

class DetectAndDropStitchingMistakes(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = DetectAndDropStitchingMistakesParameters
        super(DetectAndDropStitchingMistakes,self).__init__(schema_type=schema_type,*args,**kwargs)
    def run(self):
        print self.args
        self.logger.error('WARNING NEEDS TO BE TESTED, TALK TO FORREST IF BROKEN')
        if not os.path.isdir(self.args['jsonDirectory']):
                os.makedirs(self.args['jsonDirectory'])

        #STEP 2: get z values of stitched stack
        zvalues=renderapi.stack.get_z_values_for_stack(self.args['prestitchedStack'],render=self.render)
        
        print 'processing %d sections'%len(zvalues)
        #SETUP a processing pool to process each section
        pool =mp.ProcessingPool(self.args['pool_size'])

        #define a partial function that takes in a single z
        partial_process = partial(process_section,renderObj=render,prestitchedStack=self.args['prestitchedStack'],
            poststitchedStack=self.args['poststitchedStack'],outputStack=self.args['outputStack'],
            distance_threshold=self.args['distance_threshold'],edge_threshold=self.args['edge_threshold'])

        #parallel process all sections
        jsonfiles = pool.map(partial_process,zvalues)
        
        #create stack and upload to render
        renderapi.stack.create_stack(self.args['outputStack'], render=self.render)
        renderapi.client.import_jsonfiles_parallel(self.args['outputStack'],
                                                    jsonfiles,
                                                    render=self.render)
                                                    

if __name__ == "__main__":
    mod = DetectAndDropStitchingMistakes(input_data= example_json)
    mod.run()

  


