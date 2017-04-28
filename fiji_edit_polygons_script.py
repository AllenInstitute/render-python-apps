#import ij
from ij import IJ
import json
from ij.process import FloatPolygon
from ij.gui import PolygonRoi,Roi
from ij.gui import WaitForUserDialog
print 'start'
exampledict = [{'bounds': {u'maxX': 11501.0,
  u'maxY': 34395.0,
  u'maxZ': 0.0,
  u'minX': 1527.0,
  u'minY': -1296.0,
  u'minZ': 0.0},
 'filepath': '/nas4/data/M270907_Scnn1aTg2Tdt_13/processed/lowrescache/M270907_Scnn1aTg2Tdt_13/ALIGNEDSTACK_JAN3_DAPI_1_NORM_CONS/sections_at_0.1/000/0/0.0.png',
 'roi': {'coordinates': (((9617.0, -1296.0),
    (11047.0, 34394.0),
    (3777.0, 34394.0),
    (2997.0, -1296.0),
    (9617.0, -1296.0)),),
  'type': 'Polygon'},
 'z': 0}]

jsondir = '/nas3/data/M247514_Rorb_1/processed/shape_polygons_032717'
import os

files = os.listdir(jsondir)
files = [os.path.join(jsondir,f) for f in files]
files.sort()

for f in files:
    fp = open(f,'r')
    d=json.load(fp)
    fp.close()

    print d['filepath']
    imp=IJ.openImage(d['filepath'])
    imp.show()
    coords = d['roi']['coordinates'][0]
    img_width=imp.getWidth()
    img_height = imp.getHeight()
    
    bound_width = d['bounds']['maxX']-d['bounds']['minX']
    bound_height = d['bounds']['maxY']-d['bounds']['minY']
    
    scale = img_width*1.0/bound_width
    print 'scale',scale
    xvals = [(x-d['bounds']['minX'])*scale for x,y in coords[:-1]]
    yvals = [(y-d['bounds']['minY'])*scale  for x,y in coords[:-1]]
    print xvals,yvals
    fpoly = PolygonRoi(xvals,yvals,Roi.POLYGON)
    imp.setRoi(fpoly)
    
    dlg = WaitForUserDialog('testing')
    dlg.show()
    roi= imp.getRoi()
    fpoly=roi.getFloatPolygon()
    coords = [[]]
    for x,y in zip(fpoly.xpoints,fpoly.ypoints):
        x = (x/scale)+d['bounds']['minX']
        y = (y/scale)+d['bounds']['minY']
        coords[0].append([x,y])
    for x,y in zip(fpoly.xpoints[:1],fpoly.ypoints[:1]):
        x = (x/scale)+d['bounds']['minX']
        y = (y/scale)+d['bounds']['minY']
        coords[0].append([x,y])
    
    d['roi']['coordinates']=coords
    imp.close()
    fp = open(f,'w')
    json.dump(d,fp)
    fp.close()
    print 'done!'
