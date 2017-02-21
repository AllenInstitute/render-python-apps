import xml.etree.ElementTree as ET
from tilespec import TileSpec,Transform,AffineModel
from renderapi import Render
import os
import json
import argparse

if __name__ == '__main__':

    #inputfile='/nas/data/M247514_Rorb_1/scripts/test/out_edit2.xml'
    #inputOwner = 'Forrest'
    #inputProject = 'M247514_Rorb_1'
    #inputStack = 'REGFLATDAPI_1'
    #outputStack = 'ALIGNEDDAPI_1'
    #outputDir = '/nas/data/M247514_Rorb_1/processed/aligned_tilespecs'
    #host = 'ibs-forrestc-ux1.corp.alleninstitute.org'
    #port = 8081

    p = argparse.ArgumentParser(description="Take an existing render stack, and create a new render stack with downsampled tilespecs and create those downsampled tiles")
    p.add_argument('--inputfile',           help="Name of input xml file",default=None)
    p.add_argument('--inputOwner',          help="name of project owner to read project from",default = "Forrest")
    p.add_argument('--inputProject',        help="name of the input Project")
    p.add_argument('--inputStack',          help='name of stack to take in')
    p.add_argument('--outputStack',         help='name of stack to upload to render')
    p.add_argument('--outputDir',           help="name of the output directory", default='.')
    p.add_argument('--host',                help="host name of the render server",default="ibs-forrestc-ux1.corp.alleninstitute.org")
    p.add_argument('--port',                help="port for render server",default=8080)
    p.add_argument('--java_home',           help="directory for java jdk",default='/pipeline/renderdev/deploy/jdk1.8.0_73')
    
    p.add_argument('--verbose',             help="verbose output",default=False)
    a = p.parse_args()
    
    render = Render(a.host, a.port, a.inputOwner, a.inputProject)

    xmlroot = ET.parse(a.inputfile)
    layerset = xmlroot.find('t2_layer_set')
    layers = [t for t in layerset.getchildren() if t.tag == 't2_layer']

    finaltilespecs = []
    for i,layer in enumerate(layers):
        z = float(layer.get('z'))
        original_tilespecs=render.get_tile_specs_from_z(a.inputStack,z)
        patches = layer.findall('t2_patch')
        #print(len(patches))
        for k,patch in enumerate(patches):
            tem2tileid=patch.get('title')
            #print tem2tileid
            tilespecs=[ts for ts in original_tilespecs if tem2tileid == ts.tileId]
            assert len(tilespecs)>0,"did not find matching tile in render stack"
            ts = tilespecs[0]
            tem2tforms=patch.find('ict_transform_list')
            tform1 = patch.get('transform').lstrip('matrix(').rstrip(')').split(',')
            tform1 = map(float,tform1)
            tform1 = AffineModel(tform1[0],tform1[1],tform1[2],tform1[3],tform1[4],tform1[5])
            #print tform1
            tforms=[tform1]
            for tem2tform in tem2tforms.getchildren():
                cls=tem2tform.get('class')
                ds=tem2tform.get('data')
                tforms.append(Transform(cls,ds))
            tforms.append(tform1)
            ts.tforms=tforms
            finaltilespecs.append(ts)

