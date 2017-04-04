import json
import numpy as np
from rtree import index as rindex
import networkx as nx
import renderapi
import os
from pathos.multiprocessing import Pool
from functools import partial
from ..module.render_module import RenderModule, RenderParameters
from json_module import InputFile, InputDir
import marshmallow as mm

example_json={
        "render":{
            "host":"ibs-forrestc-ux1",
            "port":8080,
            "owner":"Forrest",
            "project":"M247514_Rorb_1",
            "client_scripts":"/var/www/render/render-ws-java-client/src/main/scripts"
        },
        "inputStack":"my example parameters",
        "jsonDirectory":"json directory to save into",
        "outputStack":"test_output",
        "edge_threshold":1843
}

class RemoveOuterTilesParameters(RenderParameters):
    pool_size  = mm.fields.Int(required=False,default=20,
        metadata={'description:':'degree of parallelism (default=20)'})
    edge_threshold  = mm.fields.Int(required=False,default=1843,
        metadata={'description:':'distance between tilespecs to consider as edges(default=1843)'})
    inputStack = mm.fields.Str(required=True,
        metadata={'description':'name of render stack to input'})
    outputStack = mm.fields.Str(required=True,
        metadata={'description':'name of render stack to output with outer tiles dropped'})    
    jsonDirectory = mm.fields.Str(required=True,
        metadata={'description:':'directory to save json files'})


class RemoveOuterTiles(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = RemoveOuterTilesParameters
        super(RemoveOuterTiles,self).__init__(schema_type=schema_type,*args,**kwargs)
    def run(self):
        print self.args
        self.logger.error('WARNING NEEDS TO BE TESTED, TALK TO FORREST IF BROKEN')

        #STEP 2: get z values of input stack
        zvalues=renderapi.stack.get_z_values_for_stack(a.inputStack,rende=self.render)

        #STEP 3: loop over z values
        jsonfiles = []
        for z in zvalues:
            #setup an Rtree to find overlapping tiles
            ridx = rindex.Index()
            #setup a graph to store overlapping tiles
            G=nx.Graph()
            Gpos = {}
            #get all the tilespecs for this z 
            tilespecs = renderapi.tilespec.get_tile_specs_from_z(a.inputStack,z,render=self.render)
            #insert them into the Rtree with their bounding boxes to assist in finding overlaps
            #label them by order in pre_tilespecs
            [ridx.insert(i,(ts.minX,ts.minY,ts.maxX,ts.maxY)) for i,ts in enumerate(tilespecs)]

            #loop over each tile in this z
            for i,ts in enumerate(tilespecs):

                #get the list of overlapping nodes
                nodes=list(ridx.intersection((ts.minX,ts.minY,ts.maxX,ts.maxY)))
                #remove itself
                nodes.remove(i)


                for node in nodes:
                    dpre=tilespecs[node].tforms[0].M[0:2,3]-tilespecs[i].tforms[0].M[0:2,3]
                    dp = np.sqrt(np.sum(dpre**2))
                    #add these nodes to the undirected graph
                    if (dp<2048*.9):
                        G.add_edge(i,node)
                Gpos[i]=((ts.minX+ts.maxX)/2,(ts.minY+ts.maxY)/2)

            #find the non-central nodes
            nodes_to_remove = []
            for node in G.nodes_iter():
                if len(G.neighbors(node))<4:
                    nodes_to_remove.append(node)
            #remove them
            [G.remove_node(node) for node in nodes_to_remove]

            #create new json files that include the
            jsonfilepath = os.path.join(a.jsonDirectory,'%s_z%04.0f.json'%(a.outputStack,z))
            renderapi.utils.renderdump(tilespecs,open(jsonfilepath ,'w'))
            jsonfiles.append(jsonfilepath)

        #create stack and upload to render
        renderapi.stack.create_stack(a.outputStack,render=self.render)
        renderapi.client.import_jsonfiles(a.outputStack,jsonfiles,render=self.render)
        

if __name__ == "__main__":
    mod = RemoveOuterTiles(input_data= example_json)
    mod.run()


