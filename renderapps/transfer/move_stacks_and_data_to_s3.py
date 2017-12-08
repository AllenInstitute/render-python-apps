import os
import re

import boto3
import botocore

from .transfer_module import RenderTransfer, RenderTransferParameters
from .move_stack import StackTransfer
from argschema.fields import Str

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
    "stack_in" : 'ALIGNMBP_deconv',
    "stack_out" : 'ALIGNMBP_deconv',
    "data_description": "s3:synaptome-playpen:",
    "upload_json": "true",
    "upload_data": "true",
    "check_only": "false"
}


class MoveStackAndDataToS3Parameters(RenderTransferParameters):
    example = Str(required=True,
        description='an example')
    default_val = Str(required=False,default="a default value",
        description='an example with a default')



class MoveStackAndDataToS3(RenderTransfer):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = MoveStackAndDataToS3Parameters
        super(MoveStackAndDataToS3,self).__init__(schema_type=schema_type,*args,**kwargs)
    def run(self):
        print self.args
        self.logger.error('WARNING NEEDS TO BE TESTED, TALK TO FORREST IF BROKEN')

        stack_move_params = dict(self.args)
        stack_move_params.pop('upload_data')
        stack_move_params.pop('check_only')
        stack_move_params['replace_chars']=True
        stack_move_params['remove_masks']=True
        submod = StackTransfer(input_data = stack_move_params,args=[])
        datalist=submod.run()

        if self.args['upload_data']:
            self.upload_to_s3(datalist)

    def upload_to_s3(self,datalist):
        s3 = boto3.resource('s3')
        bucket_name = re.match(r's3://([^/]*).*', self.args['data_description']).group(1)
        s3bucket = s3.Bucket(bucket_name)
        try:
            s3.meta.client.head_bucket(Bucket=bucket_name)
        except botocore.exceptions.ClientError as e:
            self.logger.error("Could not access bucket %s, giving up." % bucket_name)
            os.sys.exit(1)

        for (src, dest) in datalist:
            if src.startswith("file:"):
                src = src [5:]
            s3key = re.match(r's3://[^/]*/(.*)', dest).group(1)

            # Is this really the best way to do it?
            s3keyexists = True
            try:
                s3object = s3bucket.Object(s3key).load()
            except botocore.exceptions.ClientError as e:
                s3keyexists = False

            if s3keyexists:
                self.logger.info("Found %s, skipping." % dest)
            else:
                self.logger.debug("Upload %s to %s" % (src, dest))
                if not self.args['check_only']:
                    data = open(src, 'rb')
                    s3bucket.put_object(Key=s3key, Body=data)

if __name__ == "__main__":
    mod = MoveStackAndDataToS3(input_data= example_parameters)
    mod.run()
