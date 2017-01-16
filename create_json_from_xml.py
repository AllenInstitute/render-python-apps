#!/usr/bin/env python
'''
Build and import render-tilespec formatted data from trakem2 xml

'''
import os
import sys
import json
import argparse
import logging
import xml.etree.ElementTree as ET

try:
    from renderapi import Render
    from tilespec import TileSpec, Transform, AffineModel
except ImportError as e:
    logging.warning(e)
    sys.path.insert(0, '/data/array_tomography/ImageProcessing/render-python/')
    from renderapi import Render
    from tilespec import TileSpec, Transform, AffineModel


class ConversionError(Exception):
    pass


def num2str(num, digits):
    mystr = str(num)
    if digits > len(mystr):
        prefix = "0" * (digits-len(mystr))
        mystr = prefix + mystr
    return mystr

if __name__ == '__main__':

    # inputfile='/nas/data/M247514_Rorb_1/scripts/test/out_edit2.xml'
    # inputOwner = 'Forrest'
    # inputProject = 'M247514_Rorb_1'
    # inputStack = 'REGFLATDAPI_1'
    # outputStack = 'ALIGNEDDAPI_1'
    # outputDir = '/nas/data/M247514_Rorb_1/processed/aligned_tilespecs'
    # host = 'ibs-forrestc-ux1.corp.alleninstitute.org'
    # port = 8081

    p = argparse.ArgumentParser(
        description="Take an xml file and upload to render")
    p.add_argument('--inputfile', default=None, help="Name of input xml file")
    p.add_argument('--Owner', default="Forrest",
                   help="name of project owner to read project from")
    p.add_argument('--Project', help="name of the input Project")
    p.add_argument('--inputStack', help='name of input stack ')
    p.add_argument('--outputStack', help='name of stack to upload to render')
    p.add_argument('--outputDir', default=os.getcwd(),
                   help="name of the output directory")
    p.add_argument('--host',
                   default="ibs-forrestc-ux1.corp.alleninstitute.org",
                   help="host name of the render server")
    p.add_argument('--port', default=8080, help="port for render server",)
    p.add_argument('--java_home',
                   default='/pipeline/renderdev/deploy/jdk1.8.0_73',
                   help="directory for java jdk")

    p.add_argument('--client_scripts', help="location of client scripts")
    p.add_argument('-i', '--ignore_invisible', action='store_true',
                   help='do not upload invisible tiles in trakEM2 project')
    p.add_argument('--verbose', default=False, help="verbose output")
    a = p.parse_args()

    render = Render(a.host, a.port, a.Owner, a.Project, a.client_scripts)

    xmlroot = ET.parse(a.inputfile)
    layerset = xmlroot.find('t2_layer_set')
    layers = [t for t in layerset.getchildren() if t.tag == 't2_layer']

    if not os.path.isdir(a.outputDir):
        os.makedirs(a.outputDir)

    jsonfiles = []
    for i, layer in enumerate(layers):
        finaltilespecs = []
        z = float(layer.get('z'))
        original_tilespecs = render.get_tile_specs_from_z(a.inputStack, z)

        patches = layer.findall('t2_patch')
        for k, patch in enumerate(patches):
            tem2tileid = patch.get('title')
            if a.ignore_invisible:
                if bool(patch.get('visible') == 'false'):
                    logging.debug(
                        'skipping invisible patch {}'.format(tem2tileid))
                    continue

            if a.inputStack:
                tilespecs = [ts for ts in original_tilespecs
                             if tem2tileid == ts.tileId]
                if not len(tilespecs):
                    raise ConversionError(
                        'did not find matching tiles for layer '
                        'z={}, patch {} in render stack!'.format(
                            str(z), tem2tileid))
                ts = tilespecs[0]
            else:
                ts = TileSpec(z=z, width=patch.get('o_width'),
                              height=patch.get('o_height'),
                              imageUrl=patch.get('file_path'),
                              tileId=patch.get('title'))

            # TODO unwrap all transform lists
            tem2tforms = (patch.find('ict_transform_list').getchildren()
                          if patch.find('ict_transform_list')
                          else [patch.find('ict_transform')])

            # there is an Affine Transform defined in patch attributes
            tform1 = patch.get('transform').lstrip(
                'matrix(').rstrip(')').split(',')
            form1 = map(float, tform1)  # Should this def form1 or tform1?
            form1 = AffineModel(
                tform1[0], tform1[1], tform1[2],
                tform1[3], tform1[4], tform1[5])

            tforms = [form1] + [Transform(className=tform.get('class'),
                                          dataString=tform.get('data'))
                                for tform in tem2tforms]

            # TODO hack need lenscorrection.NonLinearTransform to come first
            # Does boolean sort necessarily preserve order within values?
            tforms = sorted(tforms, key=lambda x: x.className !=
                            'lenscorrection.NonLinearTransform')

            # this was the part i had commented out:
            # for tem2tform in tem2tforms.getchildren():
            #     cls=tem2tform.get('class')
            #    ds=tem2tform.get('data')
            #    tforms.append(Transform(cls,ds))
            # tforms.append(tform1)

            ts.tforms = tforms
            finaltilespecs.append(ts)

        fname = os.path.join(a.outputDir, "layer{}.json".format(
            str(i).zfill(str(len(layers)))))
        jsonfiles.append(fname)
        json_text = json.dumps([t.to_dict() for t in finaltilespecs], indent=4)

        with open(fname, 'w') as fd:
            fd.write(json_text)

    render.create_stack(a.outputStack)
    render.import_jsonfiles_parallel(
        a.outputStack, jsonfiles, client_scripts=render.DEFAULT_CLIENT_SCRIPTS)
