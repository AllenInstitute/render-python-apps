import numpy as np
import renderapi
import json
import os
from ..module.render_module import RenderTrakEM2Parameters, TrakEM2RenderModule
from ..shapely import tilespec_to_bounding_box_polygon
from AnnotationJsonSchema import AnnotationFile
from argschema.fields import Str, InputFile, OutputFile
from shapely import geometry
import lxml.etree


example_input = {
    "render": {
        "host": "ibs-forrestc-ux1",
        "port": 8080,
        "owner": "Forrest",
        "project": "M247514_Rorb_1",
        "client_scripts": "/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    "EMstack": "BIGALIGN_LENS_EMclahe_all",
    "trakem2project": "/nas4/data/EM_annotation/M247514_Rorb_1/m247514_Site3Annotation_MN.xml",
    "output_annotation_file": "/nas3/data/M247514_Rorb_1/annotation/m247514_Site3Annotation_MN_local.json",
    "output_bounding_box_file":"/nas3/data/M247514_Rorb_1/annotation/m247514_Site3Annotation_MN_bb_local.json",
    "renderHome": "/pipeline/render"
}



class AnnotationConversionError(Exception):
    pass


class ImportTrakEM2AnnotationParameters(RenderTrakEM2Parameters):
    EMstack = Str(
        required=True, description='stack to look for trakem2 patches in')
    trakem2project = InputFile(
        required=True, description='trakem2 file to read in')
    output_annotation_file = OutputFile(
        required=True, description="place to save annotation output")
    output_bounding_box_file = OutputFile(
        required=True, description="place to save bounding box output")
    

def convert_path(path, tform):
    # function to convert TEM2 path using the transformation tform
    # convert_path(path,tform):
    d = path.attrib['d'].split(' ')
    Nelem = int(np.ceil(len(d) * 1.0 / 3))
    points = np.zeros((Nelem, 2))

    for k, i in enumerate(range(0, len(d) + 1, 3)):

        if d[i] == 'M':
            points[k, :] = [float(d[i + 1]), float(d[i + 2])]
        elif d[i] == 'L':
            points[k, :] = [float(d[i + 1]), float(d[i + 2])]
        elif d[i] == 'z':
            points[k, :] = points[0, :]
    return tform.tform(points)


def convert_transform(tfs):
    tfs = tfs.replace('matrix(', '')
    tfs = tfs.replace(')', '')
    vals = tfs.split(',')
    tform = renderapi.transform.AffineModel(M00=vals[0],
                                            M10=vals[1],
                                            M01=vals[2],
                                            M11=vals[3],
                                            B0=vals[4],
                                            B1=vals[5])
    return tform


def convert_global_local_points(points, ts):
    tmp = list(ts.tforms)
    tmp.reverse()
    for t in tmp:
        points = t.inverse_tform(points)
    return points


def convert_path_to_area(path_numpy, layer_tilespecs):
    local_path_numpy = np.zeros(path_numpy.shape, path_numpy.dtype)
    point_missing = np.ones(path_numpy.shape[0], np.bool)
    path_points = [geometry.Point(a[0], a[1]) for a in path_numpy]
    local_tileIds = np.array(["" for i in range(path_numpy.shape[0])],dtype=np.object)

    for poly, ts, rts in layer_tilespecs:
        if np.sum(point_missing) == 0:
            break

        point_contained = np.array([poly.contains(p) for p in path_points])
        convert_point_mask_ind = np.where(point_missing & point_contained)[0]
        points = path_numpy[convert_point_mask_ind, :]
        if points.shape[0] > 0:
            local_points = convert_global_local_points(points, ts)
            local_path_numpy[convert_point_mask_ind, :] = local_points
            point_missing[convert_point_mask_ind] = 0
            local_tileIds[convert_point_mask_ind] = rts.tileId
    
    if np.sum(point_missing)>0:
        raise AnnotationConversionError("unable to find all points {} on the tiles given {}".format(path_numpy,[ts.tileId for poly,ts,rts in layer_tilespecs]))
    

    d = {}
    d['tileIds'] = local_tileIds
    d['local_path'] = local_path_numpy

    return d


def parse_area_lists(render_tilespecs, tem2_tilespecs, tem2_polygons, root, area_lists):
    json_output = {'area_lists': []}
    for thisid, al in enumerate(area_lists):
        areas = al.findall('t2_area')
        links = al.attrib['links']
        tform = convert_transform(al.attrib['transform'])
        area_list_d = {}
        area_list_d['oid'] = al.attrib['oid']
        area_list_d['id'] = thisid
        area_list_d['areas'] = []
        for area in areas:

            layerid = area.attrib['layer_id']

            layer = root.find('//t2_layer[@oid="%s"]' % layerid)
            patches = [patch for patch in layer.getchildren()]
            patchids = [patch.attrib['oid'] for patch in patches]
            layer_tilespecs = [(poly, ts, t) for poly, ts, t in zip(
                tem2_polygons, tem2_tilespecs, render_tilespecs) if ts.tileId in patchids]
            # reverse the tilespecs so they are encountered from top to bottom when iterated over
            layer_tilespecs.reverse()
            paths = area.findall('t2_path')
            # loop over all the paths
            for path in paths:
                # initialize the path's polygon with the entire path
                path_numpy = convert_path(path, tform)
                try:
                    d = convert_path_to_area(path_numpy, layer_tilespecs)
                except AnnotationConversionError as e:
                    raise AnnotationConversionError("error in converting synapse oid:{} id:{} on layer:{}, {}".format(al.attrib['oid'],thisid,layerid,e.args))
                area_list_d['areas'].append(d)

        json_output['area_lists'].append(area_list_d)
    return json_output


class ImportTrakEM2Annotations(TrakEM2RenderModule):
    default_schema = ImportTrakEM2AnnotationParameters
    default_output_schema = AnnotationFile

    def run(self):
        print self.args
        tem2file = self.args['trakem2project']
        trakem2dir = os.path.split(tem2file)[0]
        jsonFileOut = os.path.join(
            trakem2dir, os.path.splitext(tem2file)[0] + '.json')

        # convert the trakem2 project to a json tilespec
        self.convert_trakem2_project(tem2file, trakem2dir, jsonFileOut)

        # read in the tilespecs from the json, and parse them with api
        tsjson = json.load(open(jsonFileOut, 'r'))
        tem2_tilespecs = [renderapi.tilespec.TileSpec(
            json=tsj) for tsj in tsjson]

        # loop over the tem2 tilespecs to find the corresponding render tilespecs
        # matching based upon the filename (due to moving of the data)

        render_tilespecs = []
        for ts in tem2_tilespecs:
            pot_render_tilespecs = self.render.run(renderapi.tilespec.get_tile_specs_from_z,
                                                   self.args['EMstack'],
                                                   ts.z)
            try:
                mml=ts.ip.get(0)
            except KeyError:
                mml = ts.channels[0].ip.get(0)
                
                
            filepath = (os.path.split(mml['imageUrl'])[1]).split('_flip')[0]
            pot_filepaths = [(os.path.split(t.ip.get(0)['imageUrl'])[1]).split(
                '_flip')[0] for t in pot_render_tilespecs]
            render_tilespecs.append(next(t for t, fp in zip(
                pot_render_tilespecs, pot_filepaths) if fp == filepath))

        # convert the tem2_tilespecs to shapely polygons
        tem2_polygons = [tilespec_to_bounding_box_polygon(
            ts) for ts in tem2_tilespecs]

        # parse the TEM2 project
        root = lxml.etree.parse(open(tem2file, 'r'))

        # get the area lists
        area_lists = root.findall('//t2_area_list')
        area_lists = [al for al in area_lists if (len(al.getchildren()) > 0)]
        print 'project contains %d area lists' % len(area_lists)

        # parse the area lists into json
        json_output = parse_area_lists(
            render_tilespecs, tem2_tilespecs, tem2_polygons, root, area_lists)

        layer_sets = root.findall('//t2_layer_set')
        width = layer_sets[0].attrib['layer_width']
        height = layer_sets[0].attrib['layer_height']
        corners = np.array(
            [[0, 0], [0, height], [width, height], [width, 0], [0, 0]],dtype=np.float)
        layers = root.findall('//t2_layer')
        bounding_box_local = {'area_lists': []}
        for layer in layers:
            patches = [patch for patch in layer.getchildren()]
            patchids = [patch.attrib['oid'] for patch in patches]
            layer_tilespecs = [(poly, ts, t) for poly, ts, t
                               in zip(tem2_polygons, tem2_tilespecs, render_tilespecs)
                               if ts.tileId in patchids]
            try:
                d = convert_path_to_area(corners,layer_tilespecs)
            except AnnotationConversionError as e:
                raise AnnotationConversionError("unable to find bounding box of layer {} z={}, due to corners not being on layers with patches {} ".format(layer.attrib['oid'],layer.attrib['z'],patchids))
            area_list_d = {}
            area_list_d['oid'] = layer.attrib['oid']
            area_list_d['id'] = int(layer_tilespecs[0][2].z)
            area_list_d['areas'] = [d]
            bounding_box_local['area_lists'].append(area_list_d)
        

        self.output(bounding_box_local,self.args['output_bounding_box_file'])
        # dump the json dictionary through the AnnotationFile schema
        # in order to serialize it to disk
        self.output(json_output,self.args['output_annotation_file'])


if __name__ == "__main__":
    mod = ImportTrakEM2Annotations(input_data=example_input)
    mod.run()
