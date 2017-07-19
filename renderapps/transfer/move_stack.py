import tempfile
import os
import renderapi
from .transfer_module import RenderTransferParameters, RenderTransfer
from argschema.fields import Str, Boolean


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
    "replace_chars": "false",
    "remove_masks": "false",
    "upload_json": "true"
}
class StackTransferParameters(RenderTransferParameters):
    stack_in = Str(required=True,
        metadata={'description':'stack to move from source_render'})
    stack_out = Str(required=False,
        metadata={'description':'stack to move to target_render (default to the same)'})
    data_description = Str(required=False,default='file:',
        metadata={'description':'replace the ^.*: with this in the image url (default file:)'})
    replace_chars = Boolean(required=False,default=True,
        metadata={'description':'replace perc20 charactesr with spaces (default True)'})
    remove_masks = Boolean(required=False,default=False,
        metadata={'description':'remove the masks (default False)'})
    upload_json = Boolean(required=False,default=True,
        metadata={'description':'actually do the upload to the adjacent render,\
         false will still return list of to/from image destinations (default True)'})


class StackTransfer(RenderTransfer):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = StackTransferParameters
        super(StackTransfer,self).__init__(schema_type=schema_type,*args,**kwargs)
    def run(self):
        stack_out = self.args.get('stack_out',self.args['stack_in'])
        stack_in =self.args['stack_in']

        zvalues = renderapi.stack.get_z_values_for_stack(stack_in, render=self.render_source)

        tfiles = []

        datalist = []

        for z in zvalues:
            tilespecs = renderapi.tilespec.get_tile_specs_from_z(
                stack_in,
                z,
                render=self.render_source)
            for ts in tilespecs:
                url = ts.ip.mipMapLevels[0].imageUrl
                (precolon, postcolon) = url.split(':')
                newurl = self.args['data_description'] + postcolon

                ts.ip.mipMapLevels[0].imageUrl = newurl
                if self.args['replace_chars']:
                    url = url.replace("%20", " ")
                    newurl = newurl.replace("%20", " ")
                datalist.append((url, newurl))

                # TODO: A seperate pass for masks?
                if self.args['remove_masks']:
                    ts.ip.mipMapLevels[0].maskUrl=None
            if self.args['upload_json']:
                tid,tfile = tempfile.mkstemp(suffix='.json')
                self.logger.debug(tfile)
                fid = open(tfile,'w')
                renderapi.utils.renderdump(tilespecs,fid)
                fid.close()
                tfiles.append(tfile)
        if self.args['upload_json']:
            self.render_target.run(renderapi.stack.create_stack,stack_out)
            self.render_target.run(renderapi.client.import_jsonfiles_parallel,stack_out,tfiles)
            self.render_target.run(renderapi.stack.set_stack_state,stack_out,'COMPLETE')
                    # Clean up temp JSON files
            for filename in tfiles:
                self.logger.debug("Removing " + filename)
                os.remove(filename)
        return datalist

if __name__ == "__main__":
    mod = StackTransfer(input_data= example_parameters)
    mod.run()
