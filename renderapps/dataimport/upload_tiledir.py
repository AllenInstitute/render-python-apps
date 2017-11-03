import os
import renderapi
from renderapi.tilespec import TileSpec, Layout, MipMapLevel
from renderapi.transform import AffineModel
from create_mipmaps import create_mipmaps
my_env = os.environ.copy()
from ..module.render_module import RenderModule, RenderParameters
from argschema.fields import InputFile, InputDir, Str, Int, Boolean
import pandas as pd
import glob

example_input={
    #"statetableFile" : "/nas/data/M246930_Scnn1a_4_f1//scripts/statetable_ribbon_0_session_0_section_3",
    #"projectDirectory" : "/nas/data/M246930_Scnn1a_4_f1/",
    #"outputStackPrefix" : "Acquisition",
    #"pool_size" : 20,
    #"inputTileDirectory" : "/nas4/KDM-SYN-100430B-L5_Deconv/Curated_SJS_2017/Deconvolved/Rnd01_DAPI_461nm_deconv",
    #"tilespecDirectory" : "/nas4/KDM-SYN-100430B-L5_Deconv/Curated_SJS_2017/Deconvolved_and_Ultraligned/alignment_intermediates/tilespecs/Rnd01_DAPI",
    #"outputStack" : "Stitched_DAPI_1"
}


class UploadTileDirParameters(RenderParameters):
    inputTileDirectory = InputDir(required=True,
        description='path to project root')
    tilespecDirectory = Str(required=True,
        description='path to project root')
    outputStack = Str(required=True,
        description='Output stack')
    pool_size = Int(require=False,default=20,
        description='number of parallel threads to use')
    delete_stack = Boolean(require=False,default=True,
        description='flag to decide whether stack should be deleted before new upload')

def make_tilespec(tileDirectory,tilespecdir,outputProject,outputOwner,outputStack,minval=0,maxval=50000):
    imagefiles = glob.glob(tileDirectory + "/*.tif")
    imagefiles.sort()
    z = 0
    tilespecpaths = []
    tilespeclist = []
    for f in imagefiles:
        #print f
        filepath=f
        sectionId="SEC%04d"%z
        tileId = "%04d"%z
        frameId = "FRAME%04d"%z
        width = 1388
        height = 1040



        fileparts=filepath.split(os.path.sep)[1:]
        if not os.path.isdir(tilespecdir):
            os.makedirs(tilespecdir)

        layout = Layout(sectionId=sectionId,
                        scopeId='Leica',
                        cameraId='zyla',
                        imageRow=0,
                        imageCol=0,
                        stageX = 0.0,
                        stageY = 0.0,
                        rotation = 0.0,
                        pixelsize = 0.103)


        tform = AffineModel(M00=1.0,M01 = 0.0, M10 = 0.0, M11 = 1.0, B0 = 0.0, B1 = 0.0)
        mipmap0 = MipMapLevel(level=0,imageUrl=filepath)
        mipmaplevels=[mipmap0]

        #tilespeclist.append(TileSpec(tileId=tileId,frameId = frameId, z=z, width=width, height=height, tforms=[tform],minint=minval,maxint=maxval,layout= layout))
        t = TileSpec(tileId=tileId,frameId = frameId, z=z, width=width, height=height, mipMapLevels=mipmaplevels, tforms=[tform],minint=minval,maxint=maxval,layout= layout)
        tilespeclist.append(t)
        json_file = os.path.join(tilespecdir,outputProject+'_'+outputOwner+'_'+outputStack+'_%04d.json'%z)
        fd=open(json_file, "w")
        renderapi.utils.renderdump([t],fd)
        fd.close()
        tilespecpaths.append(json_file)
        z = z+1
    return tilespecpaths,tilespeclist


class UploadTileDir(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = UploadTileDirParameters

        super(UploadTileDir,self).__init__(schema_type=schema_type,*args,**kwargs)
    def run(self):
        outputProject=self.args['render']['project']
        outputOwner = self.args['render']['owner']
        inputTileDirectory = self.args['inputTileDirectory']
        tilespecDirectory = self.args['tilespecDirectory']
        outputStack = self.args['outputStack']
        tilespecpaths,tilespeclist = make_tilespec(inputTileDirectory,tilespecDirectory,outputProject,outputOwner,outputStack)

        #tilespecpaths=[tilespecpaths[32]]

        print tilespecpaths
        #renderapi.stack.set_stack_state(outputStack,state="COMPLETE",render=self.render)
        renderapi.stack.create_stack(outputStack,owner=outputOwner,project=outputProject,verbose=False,render=self.render)
        self.logger.info(tilespecpaths)
        #renderapi.client.import_jsonfiles(outputStack,tilespecpaths,render=self.render, poolsize=self.args['pool_size'])
        renderapi.client.import_tilespecs_parallel(outputStack,tilespeclist,render=self.render, poolsize=self.args['pool_size'])
if __name__ == "__main__":
    #mod = CreateFastStack(schema_type = CreateFastStacksParameters)
    #print example_input
    mod = UploadTileDir(input_data=example_input,schema_type=UploadTileDirParameters)
    mod.run()
