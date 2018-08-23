import os
import renderapi
from renderapi.tilespec import TileSpec, Layout
from renderapi.image_pyramid import MipMap, ImagePyramid
from renderapi.channel import Channel
from renderapi.transform import AffineModel
from create_mipmaps import create_mipmaps
my_env = os.environ.copy()
from ..module.render_module import RenderModule, RenderParameters
from argschema.fields import InputFile, InputDir, Str, Int, Boolean
import pandas as pd

example_input = {
    'render': {
        'host': '10.128.24.33',
        'port': 80,
        'owner': 'multchan',
        'project': 'M335503_Ai139_smallvol',
        'client_scripts': '/shared/render/render-ws-java-client/src/main/scripts'
    },
    "statetableFile": "/nas2/data/M335503_Ai139_smallvol/scripts/statetable_ribbon_5_session_1_section_1",
    "projectDirectory": "/nas2/data/M335503_Ai139_smallvol",
    "outputStackPrefix": "TESTAcquisition",
    "pool_size": 20,
    "delete_stack": False
}


class CreateFastStacksParameters(RenderParameters):
    statetableFile = InputFile(required=True,
                               description='state table file')
    projectDirectory = InputDir(required=True,
                                description='path to project root')
    reference_channel = Str(required=False,
                            default="DAPI",
                            description="will take the first channel which contains these letters and make it the reference image")
    outputStackPrefix = Str(required=False, default="ACQ",
                            description='prefix to include in front of channel name for render stack')
    pool_size = Int(require=False, default=20,
                    description='number of parallel threads to use')
    delete_stack = Boolean(require=False, default=True,
                           description='flag to decide whether stack should be deleted before new upload')


def make_tilespec_from_statetable(df, rootdir, outputProject, outputOwner, outputStack, reference_channel='dapi', minval=0, maxval=50000):
    df = df[df['zstack'] == 0]
    #ribbons = df.groupby('ribbon')
    # zoffset=0

    # for ribbnum,ribbon in ribbons:
    #    ribbon.loc[ribbon.index,'z']=ribbon['section']+zoffset
    #    zoffset += ribbon['section'].max()+1
    #    df.loc[ribbon.index,'z']=ribbon['z'].values

    mipmap_args = []
    tilespecpaths = []
    for (sess, chgroup) in df.groupby(['session']):
        print(sess)

        for ((rib, sect), group) in chgroup.groupby(['ribbon', 'section']):
            tilespeclist = []
            z = 0
            for frame, frame_group in group.groupby('frame'):



                channels = []
                reference_ip = None
                for ind, row in frame_group.iterrows():
                    filepath = row.full_path
                    fileparts = filepath.split(os.path.sep)[1:]
                    tilespecdir = rootdir + "/processed/downsamp_tilespec/" + \
                        fileparts[5]+"/"+fileparts[6]+"/"+fileparts[7]
                    if not os.path.isdir(tilespecdir):
                        os.makedirs(tilespecdir)
                    downdir = rootdir+"/processed/downsamp_images/" + \
                        fileparts[5]+"/"+fileparts[6]+"/"+fileparts[7]

                    if not os.path.exists(downdir):
                        os.makedirs(downdir)

                    # construct command for creating mipmaps for this tilespec
                    #downcmd = ['python','create_mipmaps.py','--inputImage',filepath,'--outputDirectory',downdir,'--mipmaplevels','1','2','3']
                    # cmds.append(downcmd)
                    mipmap_args.append((filepath, downdir))
                    ip = ImagePyramid()
                    ip[0] = MipMap(imageUrl=row.full_path)
                    filename = "%s_S%04d_F%04d_Z%02d.tif" % (
                        row.ch_name, row.section, row.frame, 0)
                    for i in range(1, 4):
                        scUrl = 'file:' + \
                            os.path.join(
                                downdir, filename[0:-4]+'_mip0%d.jpg' % i)
                        ip[i] = MipMap(imageUrl=scUrl)
                    channels.append(Channel(name=row.ch_name,
                                            ip=ip,
                                            minIntensity=minval,
                                            maxIntensity=maxval))

                    if reference_channel in row.ch_name:
                        reference_ip = ip
                        
                layout = Layout(sectionId=row.ribbon*1000+row.section,
                                scopeId='Leica',
                                cameraId='zyla',
                                imageRow=0,
                                imageCol=0,
                                stageX=row.xstage,
                                stageY=row.ystage,
                                rotation=0.0,
                                pixelsize=row.scale_x)
                tform = AffineModel(M00=row.a00,
                                    M01=row.a01,
                                    M10=row.a10,
                                    M11=row.a11,
                                    B0=row.a02,
                                    B1=row.a12)
                tilespeclist.append(TileSpec(tileId=row.tileID,
                                             frameId=row.frame,
                                             z=row.z,
                                             width=row.width,
                                             height=row.height,
                                             imagePyramid=reference_ip,
                                             channels=channels,
                                             tforms=[tform],
                                             minint=minval,
                                             maxint=maxval,
                                             layout=layout))

            json_file = os.path.join(
                tilespecdir, outputProject+'_'+outputOwner+'_'+outputStack+'_%04d.json' % z)
            fd = open(json_file, "w")
            renderapi.utils.renderdump(tilespeclist, fd)
            fd.close()
            tilespecpaths.append(json_file)
    return tilespecpaths, mipmap_args


def create_mipmap_from_tuple(mipmap_tuple):
    (filepath, downdir) = mipmap_tuple
    return create_mipmaps(filepath, downdir)


class CreateFastStack(RenderModule):
    def __init__(self, schema_type=None, *args, **kwargs):
        if schema_type is None:
            schema_type = CreateFastStacksParameters

        super(CreateFastStack, self).__init__(
            schema_type=schema_type, *args, **kwargs)

    def run(self):
        outputProject = self.args['render']['project']
        outputOwner = self.args['render']['owner']
        statetablefile = self.args['statetableFile']
        rootdir = self.args['projectDirectory']
        reference_channel = self.args['reference_channel']
        print("This is delete stack : ")
        print(self.args['delete_stack'])
        # exit(0)
        df = pd.read_csv(statetablefile)
        ribbons = df.groupby('ribbon')
        k = 0
        for ribnum, ribbon in ribbons:
            mydf = ribbon.groupby('session')
            for session, session_df in mydf:
                outputStack = self.args['outputStackPrefix'] + \
                    '_Session%d' % (session)

                self.logger.info("creating tilespecs and cmds....")
                tilespecpaths, mipmap_args = make_tilespec_from_statetable(
                    session_df, rootdir, outputProject, outputOwner, outputStack, reference_channel)
                self.logger.info("importing tilespecs into render....")
                self.logger.info("creating downsampled images ...")
                with renderapi.client.WithPool(self.args['pool_size']) as pool:
                    results = pool.map(create_mipmap_from_tuple, mipmap_args)

                # groups = [(subprocess.Popen(cmd,\
                # stdout=subprocess.PIPE) for cmd in cmds)] \
                # * self.args['pool_size'] # itertools' grouper recipe
                # for processes in izip_longest(*groups): # run len(processes) == limit at a time
                #   for p in filter(None, processes):
                #        p.wait()
                self.logger.info("uploading to render ...")
                if k == 0:
                    if self.args['delete_stack']:
                        renderapi.stack.delete_stack(
                            outputStack, owner=outputOwner, project=outputProject, render=self.render)

                    renderapi.stack.create_stack(outputStack, owner=outputOwner,
                                                 project=outputProject, verbose=False, render=self.render)
                self.logger.info(tilespecpaths)
                renderapi.client.import_jsonfiles(
                    outputStack, tilespecpaths, render=self.render, poolsize=self.args['pool_size'])
            k += 1


if __name__ == "__main__":
    #mod = CreateFastStack(schema_type = CreateFastStacksParameters)
    #print example_input
    mod = CreateFastStack(input_data=example_input,
                          schema_type=CreateFastStacksParameters)
    mod.run()
