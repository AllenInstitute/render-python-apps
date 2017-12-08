import os
import re

import boto3
import botocore

from argschema.fields import Str, Bool, List
from .transfer_module import RenderTransfer, RenderTransferParameters
from .move_stack import StackTransfer, StackTransferParametersBase

EXAMPLE_PARAMETERS = {
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
    "input_stacks" : ["ALIGNMBP_deconv"],
    "output_stacks" : ["ALIGNMBP_deconv"],
    "data_destination": "s3://synaptome-playpen:",
    "upload_json": "true",
    "upload_data": "true",
    "check_only": "false",
    "aws_region": "us-east-1"
}

class MoveStacksAndDataToS3Parameters(StackTransferParametersBase):
    check_only = Bool(required=False, default=False, description="Check for file existence but do not upload")
    upload_data = Bool(required=False, default=False, description="Upload data to S3")
    input_stacks = List(Str, required=True, description="list of stacks to copy")
    output_prefix = List(Str, required=False, description="list of names for uploaded stacks (defaults to input_stack)")
    aws_region = Str(required=False, default=None, allow_none=True, description="AWS region (required for newer regions")

class MoveStacksAndDataToS3(RenderTransfer):
    def __init__(self, schema_type=None, *args, **kwargs):
        if schema_type is None:
            schema_type = MoveStacksAndDataToS3Parameters
        super(MoveStacksAndDataToS3, self).__init__(schema_type=schema_type, *args, **kwargs)

    def run(self):
        input_stacks = self.args['input_stacks']
        output_stacks = self.args.get('output_stacks', input_stacks)

        for input_stack, output_stack in zip(input_stacks, output_stacks):
            stack_move_params = dict(self.args)
            stack_move_params['stack_in']=input_stack
            stack_move_params['stack_out']=output_stack
            stack_move_params.pop('upload_data')
            stack_move_params.pop('check_only')
            stack_move_params.pop('input_stacks')
            stack_move_params.pop('output_stacks', None)
            stack_move_params.pop('input_json', None)
            stack_move_params.pop('aws_region', None)

            submod = StackTransfer(input_data=stack_move_params, args=[])
            datalist = submod.run()

            if self.args['upload_data']:
                self.upload_to_s3(datalist)

    def upload_to_s3(self,datalist):
        s3conn = boto3.resource('s3', self.args['aws_region'])
        bucket_name = re.match(r's3://([^/]*).*', self.args['data_destination']).group(1)
        s3bucket = s3conn.Bucket(bucket_name)
        try:
            s3conn.meta.client.head_bucket(Bucket=bucket_name)
        except botocore.exceptions.ClientError as e:
            self.logger.error("Could not access bucket %s (%s), giving up.", bucket_name, e)
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
                self.logger.info("Found %s, skipping.", dest)
            else:
                self.logger.debug("Upload %s to %s", src, dest)
                if not self.args['check_only']:
                    data = open(src, 'rb')
                    s3bucket.put_object(Key=s3key, Body=data)

if __name__ == "__main__":
    mod = MoveStacksAndDataToS3(input_data=EXAMPLE_PARAMETERS)
    mod.run()
