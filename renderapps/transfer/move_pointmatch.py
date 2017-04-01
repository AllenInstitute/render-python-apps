
import os
import renderapi
from .transfer_module import RenderTransferParameters,RenderTransfer
import marshmallow as mm
from pathos.multiprocessing import Pool
from functools import partial
import json
example_parameters={
    "source_render":{
        'host':'ibs-forrestc-ux1',
        'port':80,
        'owner':'Forrest',
        'project':'M247514_Rorb_1',
        'client_scripts': '/var/www/render/render-ws-java-client/src/main/scripts'
    },
    "target_render":{
        'host':'ec2-54-202-181-130.us-west-2.compute.amazonaws.com',
        'port':8080,
        'owner':'Forrest',
        'project':'M247514_Rorb_1',
        'client_scripts': '/var/www/render/render-ws-java-client/src/main/scripts'
    },
    "collection_in" : 'ALIGNMBP_deconv',
    "collection_out" : 'ALIGNMBP_deconv',
}       
class PointMatchTransferParameters(RenderTransferParameters):
    collection_source = mm.fields.Str(required=True,
        metadata={'description':'point match collection to move from source_render'})
    collection_target = mm.fields.Str(required=False,
        metadata={'description':'point match colleciton to move to target_render (default to the same)'})
    pool_size = mm.fields.Int(required=False,default=20,
        metadata={'description':'point match colleciton to move to target_render (default to the same)'})

def process_group(render_source,collection_source,render_target,collection_target,pgroup):
    matches=renderapi.pointmatch.get_matches_with_group(collection_source,pgroup,render=render_source)
    renderapi.pointmatch.import_matches(collection_target,data=json.dumps(matches),render=render_target)

class PointMatchTransfer(RenderTransfer):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = PointMatchTransferParameters
        super(PointMatchTransfer,self).__init__(schema_type=schema_type,*args,**kwargs)

    def run(self):
        self.logger.error('WARNING NEEDS TO BE TESTED, TALK TO FORREST IF BROKEN')
        collection_target = self.args.get('collection_target',self.args['collection_source']) 
        collection_source =self.args['collection_source']

        pgroups = renderapi.pointmatch.get_match_groupIds_from_only(collection_source, render=self.render_source)

        pool = Pool(self.args['pool_size'])
        mypartial = partial(process_group,
            self.render_source,
            collection_source,
            self.render_target,
            collection_target)
        pool.map(mypartial, pgroups)
        

if __name__ == "__main__":
    mod = PointMatchTransfer(input_data= example_parameters)
    mod.run()

