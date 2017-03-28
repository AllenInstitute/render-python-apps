import marshmallow as mm
import numpy as np
class NumpyArray(mm.fields.List):
    def _deserialize(self,value,attr,obj):
        mylist = super(NumpyArray,self)._serialize(value,attr,obj)
        return np.array(mylist)
    
    def _serialize(self,value,attr,obj):
        if value is None:
            return None
        return mm.fields.List._serialize(self,value.tolist(),attr,obj)
class TilePath(mm.Schema):
    tileId = mm.fields.Str()
    z = mm.fields.Float()
    path = NumpyArray(mm.fields.List(mm.fields.Float))
class Path(mm.Schema):
    orig_path = NumpyArray(mm.fields.List(mm.fields.Float))
    tile_paths = mm.fields.Nested(TilePath,many=True)
    z = mm.fields.Float()
class Area(mm.Schema):
    layer_id = mm.fields.Str()
    paths = mm.fields.Nested(Path,many=True)
class AreaList(mm.Schema):
    style = mm.fields.Str()
    locked = mm.fields.Boolean()
    links = mm.fields.Str()
    oid = mm.fields.Str()
    transform = mm.fields.Str()
    height = mm.fields.Float()
    weight = mm.fields.Float()
    fill_paint = mm.fields.Boolean()
    layer_set_id = mm.fields.Str()
    areas = mm.fields.Nested(Area,many=True)
class AnnotationFile(mm.Schema):
    area_lists = mm.fields.Nested(AreaList,many=True)