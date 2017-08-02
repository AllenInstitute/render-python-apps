import xmltodict
import pandas as pd
import os
import numpy as np
import renderapi
import subprocess
from itertools import izip_longest
from renderapi.tilespec import TileSpec, Layout
from renderapi.transform import AffineModel
import cv2

def traverse(obj, prev_path="obj", path_repr="{}[{!r}]".format):
    if isinstance(obj, dict):
        it = obj.items()
    elif isinstance(obj, list):
        it = enumerate(obj)
    else:
        yield prev_path, obj
        return
    for k, v in it:
        for data in traverse(v, path_repr(prev_path, k), path_repr):
            yield data


def find_node_by_field(doc, field='Name', name='test'):
    for path, value in traverse(doc):
        if path.split("'")[-2] == field:
            if value == name:
                print("{} = {}".format(path, value))
                node = eval('doc' + path[3:-(len(field) + 5)])
                return node


def find_nodes_by_field(doc, field='Name', name='test'):
    nodes = []
    paths = []
    for path, value in traverse(doc):
        if path.split("'")[-2] == field:
            if value == name:
                print("{} = {}".format(path, value))
                node = eval('doc' + path[3:-(len(field) + 5)])
                nodes.append(node)
                paths.append(path)
    return nodes, paths


class AtlasTransform():
    def __init__(self, td=None):
        self.M = np.identity(4, np.double)
        if td is not None:
            tdlist = [(key, float(td[key]))
                       for key in td.keys() if key[0] == 'M']

            for key, value in tdlist:
                row = int(key[2]) - 1
                col = int(key[1]) - 1
                self.M[row, col] = value

    def load_from_openCV(self, cvm):
        self.M[0, 0] = cvm[0, 0]
        self.M[0, 1] = cvm[0, 1]
        self.M[1, 0] = cvm[1, 0]
        self.M[1, 1] = cvm[1, 1]
        self.M[0, 3] = cvm[0, 2]
        self.M[1, 3] = cvm[1, 2]
        # print self.M

    def convert_to_point_vector(self, points):
        Np = points.shape[0]

        zerovec = np.zeros((Np, 1), np.double)
        onevec = np.ones((Np, 1), np.double)

        if points.shape[1] == 2:
            Nd = 2
            points = np.concatenate((points, zerovec), axis=1)
            points = np.concatenate((points, onevec), axis=1)
        elif points.shape[1] == 3:
            points = np.concatenate((points, onevec), axis=1)
            Nd = 3
        assert(points.shape[1] == 4)
        return points, Nd

    def convert_points_vector_to_array(self, points, Nd):
        points = points[:, 0:Nd] / np.tile(points[:, 3], (Nd, 1)).T
        return points

    def tform(self, points):
        points, Nd = self.convert_to_point_vector(points)
        pt = np.dot(self.M, points.T).T
        return self.convert_points_vector_to_array(pt, Nd)

    def inverse_tform(self, points):
        points, Nd = self.convert_to_point_vector(points)
        pt = np.dot(np.linalg.inv(self.M), points.T).T
        return self.convert_points_vector_to_array(pt, Nd)

    def to_tuple(self):
        return (self.M00, self.M01, self.M10, self.M11, self.dx, self.dy)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return 'M:' + self.M.__str__()


# class Transform():
#     def __init__(self, td, pixsize, height, width):
#         self.M00 = 1.0  # float(td['M11'])
#         self.M01 = 0.0  # float(td['M12'])
#         self.M10 = 0.0  # float(td['M21'])
#         self.M11 = 1.0  # float(td['M22'])

#         self.dx = float(td['M41']) * 1000 / pixsize
#         self.dy = -float(td['M42']) * 1000 / pixsize

#     def to_tuple(self):
#         return (self.M00, self.M01, self.M10, self.M11, self.dx, self.dy)


def get_protocol(protocol_id, project):
    return find_node_by_field(project, 'UID', protocol_id)
    # prot_list=project['WorkingProtocolList']['WorkingProtocol']
    # return [p for p in prot_list if p['UID']==protocol_id][0]


def get_protocol_metadata(protocol_id, project):
    protocol = get_protocol(protocol_id, project)
    pixsize = float(protocol['Tile']['PixelSizeX']['IdealValue'])
    units = protocol['Tile']['PixelSizeX']['Units']
    width = int(protocol['Tile']['PixelCountX']['IdealValue'])
    height = int(protocol['Tile']['PixelCountY']['IdealValue'])
    if units == 'um':
        pixsize *= 1000
    if units == 'mm':
        pixsize *= 1000 * 1000

    return pixsize, width, height


def make_tile_masks(siteset, sectionset, project, project_dir):
        nodes, paths = find_nodes_by_field(project, 'Name', siteset['Name'])
        ods = [ods for ods, p in zip(nodes, paths) if 'OrderedDataSet' in p]

        if len(ods) > 0:
            # print "found it"
            ods = ods[0]

            outdir = os.path.join(os.path.join(
                project_dir, 'TEM2_import_files'))
            if not os.path.isdir(outdir):
                os.makedirs(outdir)

            for site in siteset['Site']:
                sitefile = os.path.join(
                    outdir, site['Name'].replace(' ', '') + '.csv')
                # print sitefile

                section = [section for section in sectionset['Section']
                    if section['UID'] == site['LinkedToUID']][0]
                if type(ods['PlaceableMosaic']) is not type([]):
                    ods['PlaceableMosaic'] = [ods['PlaceableMosaic']]

                mosaic = [pm for pm in ods['PlaceableMosaic'] if pm['UID']
                    == site['AcquisitionSpec']['AcquiredDataUID']]

                if len(mosaic) == 0:
                    continue
                else:
                    mosaic = mosaic[0]

                relpath = mosaic['FileName'][mosaic['FileName'].find(
                    project_base):]
                # print relpath
                unixpath = relpath.replace('\\', '/')
                unixpath = os.path.join(project_dir, unixpath)
                basedir = os.path.split(unixpath)[0]
                base = os.path.splitext(unixpath)[0]
                updatespath = base + '.ve-updates'
                with open(updatespath) as fd:
                    mosaicdoc = xmltodict.parse(fd.read())['ATLAS-Stitch-Info']
                rootdir = mosaicdoc['OriginalRoot']
                if type(mosaicdoc['Tile']) is not type([]):
                    mosaicdoc['Tile'] = [mosaicdoc['Tile']]
                cmds = []
                for i, tile in enumerate(mosaicdoc['Tile']):
                    path = os.path.join(basedir, tile['Name'] + '.tif')
                    maskpath = os.path.join(
                        basedir, tile['Name'][0:-4] + '_mask.tif')
                    flippath = os.path.join(
                        basedir, tile['Name'][0:-4] + '_flip.jpg')
                    maskcmd = ['convert', path, '-threshold', '1',
                        '-compress', 'LZW', '-depth', '8', '-flip', maskpath]
                    flipcmd = ['convert', path, '-depth', '8', '-flip',
                        '-quality', '85', '-negate', flippath]
                    # print path
                    # print maskpath
                    # print cmd
                    cmds.append(maskcmd)
                    cmds.append(flipcmd)

                    # proc=subprocess.Popen(maskcmd,stdout=subprocess.PIPE)

                    # proc.wait()
                groups = [(subprocess.Popen(cmd, stdout=subprocess.PIPE)
                         for cmd in cmds)] * 12  # itertools' grouper recipe
                # run len(processes) == limit at a time
                for processes in izip_longest(*groups):
                    for p in filter(None, processes):
                        p.wait()
                # for tile in mosaicdoc['Tiles']['Tile']:
                #    print tile['UID'],tile['@row'],tile['@col'],tile['StageX'],tile['StageY']
                # df.to_csv(sitefile,index=False,header=False)

def process_siteset(render,siteset, sectionset, project, project_path,at,lm_stack='ACQDAPI_1'):
    project_dir, project_file = os.path.split(project_path)
    project_base = os.path.splitext(project_file)[0]

    nodes, paths=find_nodes_by_field(project, 'Name', siteset['Name'])
    ods=[ods for ods, p in zip(nodes, paths) if 'OrderedDataSet' in p]
    sitename=siteset['Name'].replace(' ', '')
    json_files = []
    if len(ods) > 0:
        # print "found it"
        ods=ods[0]

        outdir=os.path.join(os.path.join(project_dir, 'TEM2_import_files'))
        if not os.path.isdir(outdir):
            os.makedirs(outdir)

        for site in siteset['Site']:
            sitefile=os.path.join(
                outdir, site['Name'].replace(' ', '') + '.csv')
            # print sitefile
            df=pd.DataFrame(columns=('Path', 'M00', 'M01',
                            'M10', 'M11', 'dx', 'dy'))

            section=[section for section in sectionset['Section']
                if section['UID'] == site['LinkedToUID']][0]
            if type(ods['PlaceableMosaic']) is not type([]):
                ods['PlaceableMosaic']=[ods['PlaceableMosaic']]

            mosaic=[pm for pm in ods['PlaceableMosaic'] if pm['UID']
                == site['AcquisitionSpec']['AcquiredDataUID']]


            if len(mosaic) == 0:
                continue
            else:
                mosaic=mosaic[0]
            # print mosaic['Name']
            # this is the transform that describes how to transform from the coodinate system of the EM stage
            # to the new coordiante transform of this mosaic site
            mt=AtlasTransform(mosaic['ParentTransform'])

            center=np.array([[0.5, 0.5]])
            center_stage=mt.tform(center)
            # these are now the light microscopy stage coordinates that correspond with this site
            lm_coords=at.inverse_tform(center_stage)
            # print mt
            # print 'center_stage',center_stage
            # print 'lm coords',lm_coords
            # print 'at',at

            # print site['AcquisitionSpec'].keys()
            pid=site['AcquisitionSpec']['WorkingProtocolUID']
            pixsize, width, height=get_protocol_metadata(pid, project)
            # print site['Name'],',',section['Name'],',',siteset['Name'],',',mosaic['Name']
            # print site['AcquisitionSpec']['AcquiredDataUID']
            relpath=mosaic['FileName'][mosaic['FileName'].find(
                project_base):]
            # print relpath
            unixpath=relpath.replace('\\', '/')
            unixpath=os.path.join(project_dir, unixpath)
            basedir=os.path.split(unixpath)[0]
            base=os.path.splitext(unixpath)[0]
            updatespath=base + '.ve-updates'
            with open(updatespath) as fd:
                mosaicdoc=xmltodict.parse(fd.read())['ATLAS-Stitch-Info']
            rootdir=mosaicdoc['OriginalRoot']
            if type(mosaicdoc['Tile']) is not type([]):
                mosaicdoc['Tile']=[mosaicdoc['Tile']]
            sectnum=int(section['SectionIndex'])
            # print 'section number',sectnum
            sectionId='%d' % (1000 * ribnum + sectnum)
            sectionZ=renderapi.stack.get_section_z_value(
                lm_stack, sectionId, render=render)
            tilespecs=renderapi.tilespec.get_tile_specs_from_z(
                lm_stack, sectionZ, render=render)
            LMtile_xy=np.array(
                [[ts['layout']['stageX'], ts['layout']['stageY']] for ts in tilespecs])
            # print LMtile_xy

            image_corners=np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
            # print "at"
            # print at
            # print "mt"
            # print mt
            tilespeclist=[]
            for i, tile in enumerate(mosaicdoc['Tile']):
                distances=np.zeros(len(tilespecs))
                imagepath=os.path.join(basedir, tile['Name'])
                maskpath=os.path.join(
                    basedir, tile['Name'][0:-4] + '_mask.tif')
                flippath=os.path.join(
                    basedir, tile['Name'][0:-4] + '_flip.jpg')
                tform=AtlasTransform(tile['ParentTransform'])
                # shift = np.array([[150,-80]])
                shift=np.array([[0, 0]])
                # tranform the EM tile through the transforms to get LM stage coordinates of corners
                EMtile_corners_lm_stage=at.inverse_tform(
                    id_at.inverse_tform(mt.tform(tform.tform(image_corners) + shift)))
                # EMtile_corners_lm_stage[:,1]+=(2048*.107)
                # EMtile_corners_lm_stage[:,1]*=-1
                # print EMtile_corners_lm_stage

                # tranform the EM tile through the transforms to get LM stage coordinates of center
                # print tform
                EMtile_center_lm_stage=at.inverse_tform(
                    id_at.inverse_tform(mt.tform(tform.tform(center) + shift)))
                # EMtile_center_lm_stage[:,1]+=(2048*.107)
                # print 'EMtile_center_lm_stage',EMtile_center_lm_stage
                # EMtile_center_lm_stage[:,1]*=-1
                # print [(ts['layout']['stageX']-tile_lm_stage[0,0])**2+(ts['layout']['stageY']+tile_lm_stage[0,1])**2 for ts in tilespecs]
                # EMtile_xy = np.array([tile_lm_stage[0,0],-tile_lm_stage[0,1]])

                # figure out which of the LM tiles is closest to this EM tile in terms of stage coordinates
                # the distance vector
                dist_xy=LMtile_xy - \
                    np.tile(EMtile_center_lm_stage, (len(tilespecs), 1))
                # the euclidean distance in microns
                d=np.sqrt(np.sum(dist_xy**2, axis=1))
                LMtile_i=np.argmin(d)  # pick out the index of the smallest
                # this is the tilespec of the closest tile
                close_spec=tilespecs[LMtile_i]
                # print 'tile ',LMtile_i,'id',close_spec['tileId'], 'closest at ','%4.2f'%d[LMtile_i],' um'
                # print close_spec

                # this calculates the delta from the EM stage coordinates to the LM stage coordinates
                # and divides by the size of LM pixels, to get delta in pixels from the center of the LM tile
                # to each of the corners of the EM tile
                # note hardcoded LM pixel size
                delt=(EMtile_corners_lm_stage - \
                        LMtile_xy[LMtile_i, :]) / 0.107
                delt_center=(EMtile_center_lm_stage - \
                                LMtile_xy[LMtile_i, :]) / 0.107

                # this is the location in terms of pixels within the LM tile of the EM corners
                # this is with pixel 0,0 in the upper left, and assuming that the stage coordinates
                # are in such a manner that positive y is down, and positive x is to the right
                EMtile_corners_local_pixels=delt + \
                    np.array(
                        [[close_spec['width'] / 2.0, close_spec['height'] / 2.0]])
                EMtile_center_local_pixels=delt_center + \
                    np.array(
                        [[close_spec['width'] / 2.0, close_spec['height'] / 2.0]])

                # use renderapi to map these local pixel coordinates to the global space
                EMtile_corners_world_coords=renderapi.coordinate.local_to_world_coordinates_array(
                    lm_stack, EMtile_corners_local_pixels, close_spec['tileId'], sectionZ,render=render)
                EMtile_center_world_coords=renderapi.coordinate.local_to_world_coordinates_array(
                    lm_stack, EMtile_center_local_pixels, close_spec['tileId'], sectionZ,render=render)
                # print "EMtile_center_world_coords",EMtile_center_world_coords

                # these are the local coordinates of the corners of the EM tile
                # listed in the same order as the "corners" variable, but noting
                # that the definition in what is 0,0 is different from ATLAS definition
                # this transformation of the tile needs to account for this
                EMpixel_corners=np.array([
                                    [0.0, float(tile['Height'])],
                                    [0.0, 0.0],
                                    [float(tile['Width']),
                                            float(tile['Height'])],
                                    [float(tile['Width']), 0]
                                ])
                # print "from\n",EMpixel_corners
                # print "to\n",EMtile_corners_world_coords
                emtform=cv2.getAffineTransform(np.float32(
                    EMpixel_corners[0:3, :]), np.float32(EMtile_corners_world_coords[0:3, :]))
                atlas_emt=AtlasTransform()
                atlas_emt.load_from_openCV(emtform)
                # print atlas_emt.tform(np.array([[0,0],[5000,5000],[0,5000],[5000,0]]))
                s=np.sqrt(-np.linalg.det(atlas_emt.M[0:2, 0:2]))
                # print atlas_emt.M[0:2,0:2]/s

                row, col=tile['Name'].split('_')[1].split('-')
                row=int(row[1:])
                col=int(col[1:])

                layout=Layout(sectionId=sectionId,
                                scopeId="Gemini",
                                cameraId='SEM3nm5K',
                                imageRow=row,
                                imageCol=col,
                                stageX=tform.tform(center)[0, 0],
                                stageY=tform.tform(center)[0, 1],
                                rotation=0.0,
                                pixelsize=0.03)
                flip=AffineModel(M00=1,
                                    M01=0,
                                    M10=0,
                                    M11=1,
                                    B0=5000 * (col - 1),
                                    B1=-5000 * (row - 1))

                am=AffineModel(M00=emtform[0, 0],
                                    M01=emtform[0, 1],
                                    M10=emtform[1, 0],
                                    M11=emtform[1, 1],
                                    B0=emtform[0, 2],
                                    B1=emtform[1, 2])

                amf=AffineModel(M00=emtform[0, 0],
                                    M01=emtform[0, 1],
                                    M10=-emtform[1, 0],
                                    M11=-emtform[1, 1],
                                    B0=emtform[0, 2],
                                    B1=emtform[1, 2])
                tilespec=TileSpec(tileId=tile['UID'],
                                    z=sectionZ,
                                    width=int(tile['Width']),
                                    height=int(tile['Height']),
                                    imageUrl='file:' + \
                                        flippath.replace(" ", "%20"),
                                    frameId=tile['UID'],
                                    maskUrl='file:' + \
                                        maskpath.replace(" ", "%20"),
                                    tforms=[amf],
                                    minint=0,
                                    maxint=255,
                                    layout=layout)
                tilespeclist.append(tilespec)
                # row= (str(path),) + tform.to_tuple()
                # df.loc[i]=row
                # print tilespec.to_dict()
            # for tile in mosaicdoc['Tiles']['Tile']:
            #    print tile['UID'],tile['@row'],tile['@col'],tile['StageX'],tile['StageY']
            # df.to_csv(sitefile,index=False,header=False)
   
            json_file=os.path.join(
                tilespec_path, 'EM_rib%04dsect%04d_%s.json' % (ribnum, sectnum, sitename))
            with open(json_file,'w') as fp:
                renderapi.utils.renderdump(tilespeclist,fp)
            json_files.append(json_file)
    return json_files
