import numpy as np
from renderapi.transform import AffineModel
import json
from functools import partial
import argparse
from renderapi.utils import stripLogger
import os
import renderapi
from ..module.render_module import RenderModule, RenderParameters
from json_module import InputFile, InputDir
import marshmallow as mm
from functools import reduce
import operator

#modified by sharmi

example_json={
    "render":{
        "host":"http://ibs-forrestc-ux1",
        "port":80,
        "owner":"S3_Run1",
        "project":"S3_Run1_Rosie",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    "input_collection_list":"Subvolume_A_Rough_Aligned_140_to_141_3D_DAPI_1,Subvolume_A_Rough_Aligned_140_to_141_3D_GFP",
	"output_collection": "Subvolume_A_Rough_Aligned_140_to_141_3D",
	"reference_channel": "DAPI_1",
    "pool_size":1
}
class ConsolidatePointMatchesAcrossChannelsParameters(RenderParameters):
    input_collection_list = mm.fields.Str(required=True,
        metadata={'description':'stack to consolidate'})
    output_collection = mm.fields.Str(required=False,
        metadata={'description':'name of output stack (default to adding postfix to input)'})
    reference_channel = mm.fields.Str(required=True,
        metadata={'description':'reference channel'})
    pool_size = mm.fields.Int(required=False, default=20,
        metadata={'description':'name of output stack (default to adding postfix to input)'})


def adjust_channel_character(m):
	#make the last character 0
	m = m[:len(m)-1]+"0"
	return m

def remove_channel_postfix(g,ref_channel):
	#remove everything after the hyphen
	ind = g.index('-')
	g = g[:ind]+"-%s"%ref_channel
	return g

def process_match(r,output_matchcollection,default_collection,ref_channel,match):
	pairs = []
	match['pId'] = adjust_channel_character(match['pId'])
	match['qId'] = adjust_channel_character(match['qId'])
	match['pGroupId'] = remove_channel_postfix( match['pGroupId'],ref_channel)
	match['qGroupId'] = remove_channel_postfix( match['qGroupId'],ref_channel)
	
	
	def_match = renderapi.pointmatch.get_matches_from_tile_to_tile(default_collection, match['pGroupId'], match['pId'], match['qGroupId'], match['qId'], render=r)
	
	print match
	
	if len(def_match)> 0:
	
		dmatch = def_match[0]
		
		print match['matches']['p'][0]
		
		match['matches']['p'][0] = match['matches']['p'][0] + dmatch['matches']['p'][0]
		match['matches']['p'][1] = match['matches']['p'][1] + dmatch['matches']['p'][1]
		match['matches']['q'][0] = match['matches']['q'][0] + dmatch['matches']['q'][0]
		match['matches']['q'][1] = match['matches']['q'][1] + dmatch['matches']['q'][1]
		match['matches']['w'][0] = match['matches']['w'][0] + dmatch['matches']['w'][0]
		
		print dmatch['matches']['p'][0]
		print match['matches']['p'][0]
		#print len(def_match)
		
		
	pairs.append(match)
	r.run(renderapi.pointmatch.import_matches,output_matchcollection,json.dumps(pairs))
	exit(0)
	return match
        	
class ConsolidatePointMatchesAcrossChannels(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = ConsolidatePointMatchesAcrossChannelsParameters
        super(ConsolidatePointMatchesAcrossChannels,self).__init__(schema_type=schema_type, *args, **kwargs)
    def run(self):
        self.logger.error('Added by Sharmi...........')
        input_collection_list = self.args['input_collection_list']
        output_collection= self.args.get('output_collection')
        inputs = input_collection_list.split(',')
        
        
        #for i in range(1,len(inputs)):
        
        for i in range(0,1):
			matches = []
			default_collection = inputs[i]
			for j in range(1,len(inputs)):
				if (i == j):
					print "i == j"
				else:
					col = inputs[j]
					groups = renderapi.pointmatch.get_match_groupIds(col,render=self.render)
					print col
					print len(groups)
					for j in range(0,len(groups)):
						print col
						print groups[j]
						matches.append(renderapi.pointmatch.get_matches_with_group(col,groups[j],render=self.render))

					matches = reduce(operator.concat,matches)
        
        
					#process_match(self.render, output_collection,default_collection,self.args['reference_channel'],matches[0])
        
        
					matcharray = []
					mypartial = partial(process_match,self.render,output_collection,default_collection,self.args['reference_channel'])
        
					with renderapi.client.WithPool(self.args['pool_size']) as pool:
						matcharray.append(pool.map(mypartial,matches))
        
        
		#print output_collection
        
        
        
if __name__ == "__main__":
    mod = ConsolidatePointMatchesAcrossChannels(input_data=example_json)
    #mod = ConsolidateTransforms(schema_type=ConsolidateTransformsParameters)
    mod.run()

    
