import xml.etree.ElementTree as ET

import sys
sys.path.insert(0,'/data/array_tomography/ImageProcessing/render-python/')

from renderapi import Render
from tilespec import TileSpec,Transform,AffineModel
import os
import json
import argparse

def num2str(num,digits):
    mystr=str(num)
    if digits>len(mystr):
        prefix = "0"* (digits-len(mystr))
        mystr = prefix + mystr
    return mystr

if __name__ == '__main__':

    #inputfile='/nas/data/M247514_Rorb_1/scripts/test/out_edit2.xml'
    #inputOwner = 'Forrest'
    #inputProject = 'M247514_Rorb_1'
    #inputStack = 'REGFLATDAPI_1'
    #outputStack = 'ALIGNEDDAPI_1'
    #outputDir = '/nas/data/M247514_Rorb_1/processed/aligned_tilespecs'
    #host = 'ibs-forrestc-ux1.corp.alleninstitute.org'
    #port = 8081

    p = argparse.ArgumentParser(description="Take an xml file and upload to render")
    p.add_argument('--inputfile',           help="Name of input xml file",default=None)
    p.add_argument('--Owner',          help="name of project owner to read project from",default = "Forrest")
    p.add_argument('--Project',        help="name of the input Project")
    p.add_argument('--inputStack',         help='name of input stack ')
    p.add_argument('--outputStack',         help='name of stack to upload to render')
    p.add_argument('--outputDir',           help="name of the output directory", default='.')
    p.add_argument('--host',                help="host name of the render server",default="ibs-forrestc-ux1.corp.alleninstitute.org")
    p.add_argument('--port',                help="port for render server",default=8080)
    p.add_argument('--java_home',           help="directory for java jdk",default='/pipeline/renderdev/deploy/jdk1.8.0_73')
    
    p.add_argument('--verbose',             help="verbose output",default=False)
    a = p.parse_args()
    
    render = Render(a.host, a.port, a.Owner, a.Project)

    xmlroot = ET.parse(a.inputfile)
    layerset = xmlroot.find('t2_layer_set')
    layers = [t for t in layerset.getchildren() if t.tag == 't2_layer']

    if not os.path.exists(a.outputDir):
	os.mkdir (a.outputDir)

    jsonfiles = []
    for i,layer in enumerate(layers):
	finaltilespecs = []
        z = float(layer.get('z'))
	print a.inputStack
	print z
        original_tilespecs=render.get_tile_specs_from_z(a.inputStack,z)
	
        patches = layer.findall('t2_patch')
        #print(len(patches))
        for k,patch in enumerate(patches):
            tem2tileid=patch.get('title')
            print tem2tileid
            tilespecs=[ts for ts in original_tilespecs if tem2tileid == ts.tileId]
            assert len(tilespecs)>0,"did not find matching tile in render stack"
            ts = tilespecs[0]
            tem2tforms=patch.find('ict_transform_list')
            tform1 = patch.get('transform').lstrip('matrix(').rstrip(')').split(',')
            form1 = map(float,tform1)
            form1 = AffineModel(tform1[0],tform1[1],tform1[2],tform1[3],tform1[4],tform1[5])
            #print tform1
            tforms=[form1]

	    #this was the part i had commented out:
            #for tem2tform in tem2tforms.getchildren():
            #    cls=tem2tform.get('class')
            #    ds=tem2tform.get('data')
            #    tforms.append(Transform(cls,ds))
            #tforms.append(tform1)
	    #######################################	

            ts.tforms=tforms
            finaltilespecs.append(ts)
	    

	#print finaltilespecs[0].to_dict()

	fname=a.outputDir+"/layer"+num2str(i,4)+".json"
	jsonfiles.append(fname)
	json_text=json.dumps([t.to_dict() for t in finaltilespecs],indent=4)
	fd=open(fname, "w")
        fd.write(json_text)
        fd.close()

    render.create_stack(a.outputStack)
    #render.import_jsonfiles_one_by_one(a.outputStack,jsonfiles)
    render.import_jsonfiles_parallel(a.outputStack,jsonfiles)



   


		

