import renderapi
import numpy as np
import marshmallow as mm
from ..module.render_module import RenderModule,RenderParameters
from functools import partial
import os
import tifffile

parameters={
    'render':{
        'host':'ibs-forrestc-ux1',
        'port':80,
        'owner':'Forrest',
        'project':'M247514_Rorb_1',
        'client_scripts':'/var/www/render/render-ws-java-client/src/main/scripts'
    },
    'stack':'BIGALIGN2_MARCH24c_MBP_deconvnew',
    'channel':'MBP_deconv',
    'minX':198908,
    'minY':-140278,
    'width':20600,
    'height':17333,
    'minZ':0,
    'maxZ':49,
    'minIntensity':0,
    'maxIntensity':255,
    'scale':0.03,
    'volume_dir':'/nas3/M247514_Rorb_1/processed/StephenVolume/',
    'pool_size':5
}

class RenderStackParameters(RenderParameters):
    stack = mm.fields.Str(required=True,
        metadata={'description':'stack to render'})
    channel = mm.fields.Str(required=False,
        metadata={'description':'name to use instead of stack to name files/directories'})
    minX = mm.fields.Int(required=False,
        metadata={'description':'minimum X of box (else default to stack bounds)'})
    minY = mm.fields.Int(required=False,
        metadata={'description':'minimum Y of box (else default to stack bounds)'})
    width = mm.fields.Int(required=False,
        metadata={'description':'width of box (else default to stack bounds)'})
    height = mm.fields.Int(required=False,
        metadata={'description':'height of box (else default to stack bounds)'})
    scale = mm.fields.Float(required=False,default=1.0,
        metadata={'description':'scale to render (default is 1.0)'})
    minZ = mm.fields.Int(required=False,
        metadata={'description':'minimum Z to use to render (default to stack bounds)'})
    maxZ = mm.fields.Int(required=False,
        metadata={'description':'maximum Z to use to render (default to stack bounds)'})
    minIntensity = mm.fields.Int(required=False,default=0,
        metadata={'description':'minimum Intensity used to render tiles(default to 0)'})
    maxIntensity = mm.fields.Int(required=False,default=65535,
        metadata={'description':'maximum Intensity used to render tiles(default to 65535)'})

    volume_dir = mm.fields.Str(required=True,
        metadata={'description':'root folder to save images.. volume_dir/channel/channel_XXXXXX.tif'})
    pool_size = mm.fields.Int(required=False,default=5,
        metadata={'description':'degree of parallelism to use (default to 5)'})



def process_z(render,stack,channel,save_dir,x,y,width,height,scale,minIntensity,maxIntensity,z,img_format='png'):
    img = renderapi.image.get_bb_image(stack,z,x,y,width,height,
                                        scale=scale,
                                        minIntensity=minIntensity,
                                        maxIntensity=maxIntensity,
                                        img_format=img_format,
                                        render=render)
    img = img[:,:,0]
    filepath = os.path.join(save_dir,'%s_%06d.tif'%(channel,z))
    tifffile.imsave(filepath,img)
    return filepath



class RenderStack(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = RenderStackParameters
        super(RenderStack,self).__init__(schema_type=schema_type,*args,**kwargs)
    def run(self):
        #process defaults
        stackBounds = renderapi.stack.get_stack_bounds(self.args['stack'],render=self.render)
        stack_width = stackBounds['maxX']-stackBounds['minX']
        stack_height = stackBounds['maxY']-stackBounds['minY']
        width = self.args.get('width',stack_width)
        height = self.args.get('height',stack_height)
        minX = self.args.get('minX',stackBounds['minX'])
        minY = self.args.get('minY',stackBounds['minY'])

        #get defaults for z values
        zvalues = renderapi.stack.get_z_values_for_stack(self.args['stack'],render=self.render)
        zvalues = np.array(zvalues)
        minZ = self.args.get('minZ',np.min(zvalues))
        maxZ = self.args.get('maxZ',np.max(zvalues))
        zvalues=zvalues[zvalues>=minZ]
        zvalues=zvalues[zvalues<=maxZ]


        channel = self.args.get('channel',self.args['stack'])

        stack_dir = os.path.join(self.args['volume_dir'],channel)
        if not os.path.isdir(stack_dir):
            os.makedirs(stack_dir)
        self.logger.debug('DownloadVolume: stack_dir {}'.format(stack_dir))

        my_partial = partial(process_z,
                             self.render,
                             self.args['stack'],
                             channel,
                             stack_dir,
                             minX,
                             minY,
                             width,
                             height,
                             self.args['scale'],
                             self.args['minIntensity'],
                             self.args['maxIntensity'])
        with renderapi.client.WithPool(self.args['pool_size']) as pool:
            files = pool.map(my_partial,zvalues)
        self.logger.debug('DownloadVolue:saved files {}'.format(files))


if __name__=='__main__':
    mod = RenderStack(input_data = parameters)
    mod.run()
