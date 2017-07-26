import argschema
import numpy as np


class NumpyArray(argschema.fields.List):
    def _deserialize(self, value, attr, obj):
        mylist = super(NumpyArray, self)._serialize(value, attr, obj)
        return np.array(mylist)

    def _serialize(self, value, attr, obj):
        if value is None:
            return None
        return argschema.fields.List._serialize(
            self, value.tolist(), attr, obj)


class TilePath(argschema.schemas.mm.Schema):
    tileId = argschema.fields.Str()
    z = argschema.fields.Float()
    path = NumpyArray(argschema.fields.List(argschema.fields.Float))


class Path(argschema.schemas.mm.Schema):
    orig_path = NumpyArray(argschema.fields.List(argschema.fields.Float))
    tile_paths = argschema.fields.Nested(TilePath, many=True)
    z = argschema.fields.Float()


class Area(argschema.schemas.mm.Schema):
    layer_id = argschema.fields.Str()
    paths = argschema.fields.Nested(Path, many=True)


class AreaList(argschema.schemas.mm.Schema):
    style = argschema.fields.Str()
    locked = argschema.fields.Boolean()
    links = argschema.fields.Str()
    oid = argschema.fields.Str()
    transform = argschema.fields.Str()
    height = argschema.fields.Float()
    weight = argschema.fields.Float()
    fill_paint = argschema.fields.Boolean()
    layer_set_id = argschema.fields.Str()
    areas = argschema.fields.Nested(Area, many=True)


class AnnotationFile(argschema.schemas.mm.Schema):
    area_lists = argschema.fields.Nested(AreaList, many=True)
