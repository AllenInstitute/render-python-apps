import tempfile
import os
import argparse
import re

import logging
import renderapi
import boto3
import botocore

#
# Kludgey script to query a local stack and then:
# A) upload JSON to a remote cloud instance (--upload-json) wit
# B) upload to S3
#

# logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

#CLIENT_SCRIPTS='/Users/eric/code/render/render-ws-java-client/src/main/scripts'
CLIENT_SCRIPTS='/var/www/render/render-ws-java-client/src/main/scripts'

render1params = {
    'host':'ibs-forrestc-ux1',
    'port':80,
    'owner':'Forrest',
    'project':'M247514_Rorb_1',
    'client_scripts': CLIENT_SCRIPTS
}
render2params = {
    #'host':'54.190.3.29',
    'host':'ec2-54-202-181-130.us-west-2.compute.amazonaws.com',
    'port':8080,
    'owner':'Forrest',
    'project':'M247514_Rorb_1',
    'client_scripts': CLIENT_SCRIPTS
}

# Use to test upload
# stack_in = 'ALIGNEM_reg2_clahe'
stack_in = 'ALIGNMBP_deconv'
# stack_in = 'ALIGNPSD95_deconv'
# stack_in = 'ALIGNEM_reg2_clahe'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--upload-json", action='store_true')
    parser.add_argument("--upload-data", action='store_true')
    parser.add_argument("--check-only", action='store_true', help="Check s3 data files but don't upload")
    parser.add_argument("--data-destination", default="s3://synaptomes-playpen")

    args = parser.parse_args()

    render = renderapi.render.connect(**render1params)
    zvalues = renderapi.stack.get_z_values_for_stack(stack_in,render=render)

    tfiles = []

    datalist = []

    for z in zvalues:
        tilespecs = renderapi.tilespec.get_tile_specs_from_z(stack_in,z,render=render)
        for ts in tilespecs:
            url = ts.ip.mipMapLevels[0].imageUrl
            newurl = url.replace('file:',args.data_destination)
            ts.ip.mipMapLevels[0].imageUrl = newurl
            url = url.replace("%20", " ")
            newurl = newurl.replace("%20", " ")
            datalist.append((url, newurl))

            # TODO: A seperate pass for masks?
            ts.ip.mipMapLevels[0].maskUrl=None
        tid,tfile = tempfile.mkstemp(suffix='.json')
        print(tfile)
        fid = open(tfile,'w')
        renderapi.utils.renderdump(tilespecs,fid)
        fid.close()
        tfiles.append(tfile)

      # Delete and recreate stack on cloud
    if args.upload_json:
        render2 = renderapi.render.connect(**render2params)
        renderapi.stack.create_stack(stack_in,render=render2)
        renderapi.stack.delete_stack(stack_in,render=render2)
        renderapi.stack.create_stack(stack_in,render=render2)
        renderapi.client.import_jsonfiles_parallel(stack_in,tfiles,render=render2)
        renderapi.stack.set_stack_state(stack_in,'COMPLETE',render=render2)

    if args.upload_data:
        s3 = boto3.resource('s3')
        bucket_name = re.match(r's3://([^/]*).*', args.data_destination).group(1)
        s3bucket = s3.Bucket(bucket_name)
        try:
            s3.meta.client.head_bucket(Bucket=bucket_name)
        except botocore.exceptions.ClientError as e:
            print("Could not access bucket %s, giving up." % bucket_name)
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
                print("Found %s, skipping." % dest)
            else:
                print("Upload %s to %s" % (src, dest))
                if not args.check_only:
                    data = open(src, 'rb')
                    s3bucket.put_object(Key=s3key, Body=data)
          
    # Clean up temp JSON files
    for filename in tfiles:
        print("Removing " + filename)
        os.remove(filename)
        
if __name__ == "__main__":
    main()
