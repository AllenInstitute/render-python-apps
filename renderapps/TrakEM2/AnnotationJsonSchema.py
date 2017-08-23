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

class Area(argschema.schemas.mm.Schema):
    tileId = argschema.fields.Str()
    local_path = NumpyArray(argschema.fields.List(argschema.fields.Float))
    global_path = NumpyArray(argschema.fields.List(argschema.fields.Float))

class AreaList(argschema.schemas.mm.Schema):
    oid = argschema.fields.Str()
    id = argschema.fields.Int(required=True)
    areas = argschema.fields.Nested(Area, many=True)

class AnnotationFile(argschema.schemas.mm.Schema):
    area_lists = argschema.fields.Nested(AreaList, many=True)
