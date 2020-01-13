from canoser.cursor import Cursor
from io import StringIO
import json

class Base:
    """
    All types should implment following four methods:

    def encode(cls_or_obj, value)

    def decode(cls_or_obj, cursor)

    def check_value(cls_or_obj, value)

    def to_json_serializable(cls_or_obj, value)
    """


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
        return self.to_json(indent=2)

    def to_json(self, sort_keys=False, indent=4):
        amap = self.to_json_serializable()
        return json.dumps(amap, sort_keys=sort_keys, indent=indent)
