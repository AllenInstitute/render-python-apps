import tempfile
import os
import sets
import renderapi
from .transfer_module import RenderTransferParameters, RenderTransfer
from argschema.fields import Str, Boolean


EXAMPLE_PARAMETERS = {
    "render_source":{
        "host":"ibs-forrestc-ux1",
        "port":80,
        "owner":"Forrest",
        "project":"M247514_Rorb_1",
        "client_scripts": "/var/www/render/render-ws-java-client/src/main/scripts"
    },
    "render_target":{
        "host":"ec2-54-202-181-130.us-west-2.compute.amazonaws.com",
        "port":8080,
        "owner":"Forrest",
        "project":"M247514_Rorb_1",
        "client_scripts": "/var/www/render/render-ws-java-client/src/main/scripts"
    },
    "stack_in" : "ALIGNMBP_deconv",
    "stack_out" : "ALIGNMBP_deconv",
    "data_destination": "s3://synaptome-playpen",
    "remove_masks": "false",
    "upload_json": "false",
    "rewrite_urls": "true"
}

class StackTransferParametersBase(RenderTransferParameters):
    data_destination = Str(required=False,default='file:',
        description='replace the ^.*: with this in the image url (default file:)')
    remove_masks = Boolean(required=False,default=False,
        description='remove the masks (default False)')
    upload_json = Boolean(required=False,default=True,
        description='actually do the upload to the adjacent render,\
         false will still return list of to/from image destinations (default True)')
    rewrite_urls = Boolean(required=False,default=True, description='rewrite URLs; required for data upload (default true)')

class StackTransferParameters(StackTransferParametersBase):
    stack_in = Str(required=True,
        description='stack to move from source_render')
    stack_out = Str(required=False,
        description='stack to move to target_render (default to the same)')

class StackTransfer(RenderTransfer):
    def __init__(self, schema_type=None, *args, **kwargs):
        if schema_type is None:
            schema_type = StackTransferParameters
        super(StackTransfer,self).__init__(schema_type=schema_type,*args,**kwargs)
    
        self.tfiles = []
        self.datalist = []
        self.seen_urls = sets.Set()

    def sanitizeURL(self, url):
        """Normalize urls into a clean file:/path/form.jpg url."""
        if url is None or url == "":
            return None
        if url[0] == "/":
            url = "file:" + url
        # file:/// are also used (and valid)
        url = url.replace('file:///', 'file:/')
        # Clean up double slashes
        while "//" in url:
            url = url.replace('//', '/')
        # Use proper spaces
        url = url.replace("%20", " ")
        return url

    def transformURL(self, url):
        """Calculate new path and update worklists."""
        if self.args['rewrite_urls']:
            url = self.sanitizeURL(url)
            (precolon, postcolon) = url.split(':')
            newurl = self.args['data_destination'] + postcolon
        else:
            newurl = url

        if newurl not in self.seen_urls:
            self.datalist.append((url, newurl))
            self.seen_urls.add(newurl)

        # Replace spaces with %20 -- may be needed for ImageJ url.open?
        newurl.replace(" ", "%20")
        return newurl

    def transform_ip(self, ip):
        """Find and adjust all of the URLs associated with an ImageProcessor"""
        for level in ip.values():
            level.imageUrl = self.transformURL(level.imageUrl)
            if self.args['remove_masks']:
                level.maskUrl = None
            else:
                level.maskUrl = self.transformURL(level.maskUrl)

    def run(self):
        stack_out = self.args.get('stack_out',self.args['stack_in'])
        stack_in =self.args['stack_in']

        zvalues = renderapi.stack.get_z_values_for_stack(stack_in, render=self.render_source)

        for z in zvalues:
            tilespecs = renderapi.tilespec.get_tile_specs_from_z(
                stack_in, z, render=self.render_source)
            for ts in tilespecs:
                self.transform_ip(ts.ip)
                if ts.channels is not None:
                    for chan in ts.channels:
                        self.transform_ip(chan.ip)                          
            if self.args['upload_json']:
                tid,tfile = tempfile.mkstemp(suffix='.json')
                self.logger.debug(tfile)
                fid = open(tfile,'w')
                renderapi.utils.renderdump(tilespecs,fid)
                fid.close()
                self.tfiles.append(tfile)

        if self.args['upload_json']:
            self.render_target.run(renderapi.stack.create_stack, stack_out)
            self.render_target.run(renderapi.client.import_jsonfiles, stack_out, self.tfiles)
            self.render_target.run(renderapi.stack.set_stack_state, stack_out, 'COMPLETE')
            # Clean up temp JSON files
            for filename in self.tfiles:
                self.logger.debug("Removing " + filename)
                os.remove(filename)
        return self.datalist

if __name__ == "__main__":
    mod = StackTransfer(input_data=EXAMPLE_PARAMETERS)
    mod.run()
