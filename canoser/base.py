from canoser.cursor import Cursor
from io import StringIO
import json

class Base:

    def serialize(self):
        return self.__class__.encode(self)

    @classmethod
    def deserialize(cls, buffer, check=True):
        cursor = Cursor(buffer)
        ret = cls.decode(cursor)
        if not cursor.is_finished() and check:
            raise IOError("bytes not all consumed:{}, {}".format(
                len(buffer), cursor.offset))
        return ret

    def __str__(self):
        concat = StringIO()
        self.__class__.pretty_print_obj(self, concat, 0)
        return concat.getvalue()

    def to_json(self, sort_keys=False, indent=4):
        amap = self.to_json_serializable()
        return json.dumps(amap, sort_keys=sort_keys, indent=indent)

    @staticmethod
    def to_json_data(base=None, value_type=None):
        if base is not None:
            return base.to_json_serializable()
        value, atype = value_type
        if hasattr(value, "to_json_serializable"):
            return value.to_json_serializable()
        if hasattr(atype, "to_json_serializable"):
            return atype.to_json_serializable(value)
        return value