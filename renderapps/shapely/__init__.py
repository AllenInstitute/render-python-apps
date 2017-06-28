from shapely import geometry
import numpy as np
#function to convert a tilespec to a shapely polygon with its corners in global coordinates
def tilespec_to_bounding_box_polygon(ts):
    corners=np.array([[0,0],[0,ts.height],[ts.width,ts.height],[ts.width,0]])
    for tform in ts.tforms:
        corners=tform.tform(corners)
    return geometry.Polygon(corners) 