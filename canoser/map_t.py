from canoser.base import Base
from canoser.int_type import Uint32

class MapT:

    def __init__(self, ktype, vtype):
        self.ktype = ktype
        self.vtype = vtype

    def encode(self, kvs):
        output = b""
        output += Uint32.encode(len(kvs))
        odict = {}
        for k, v in kvs.items():
            odict[self.ktype.encode(k)] = self.vtype.encode(v)
        for name in sorted(odict.keys()):
            output += name
            output += odict[name]
        return output

    def decode(self, cursor):
        kvs = {}
        size = Uint32.decode(cursor)
        for _ in range(size):
            k = self.ktype.decode(cursor)
            v = self.vtype.decode(cursor)
            if isinstance(k, list) and isinstance(k[0], int):
                #python doesn't support list as key in dict, so we change list to bytes
                kvs[bytes(k)] = v
            else:
                kvs[k] = v
        return kvs

    def check_value(self, kvs):
        if not isinstance(kvs, dict):
            raise TypeError(f"{kvs} is not a dict.")
        for k, v in kvs.items():
            if isinstance(self.ktype, list) or \
                (hasattr(self.ktype, 'delegate_type') and isinstance(self.ktype.delegate_type, list)):
                from canoser.types import BytesT
                BytesT.check_value(k)
            else:
                self.ktype.check_value(k)
            self.vtype.check_value(v)

    def __eq__(self, other):
        if not isinstance(other, MapT):
            return False
        return self.ktype == other.ktype and self.vtype == other.vtype

    def pretty_print_obj(cls, obj, buffer, ident):
        prefix_blank = '  '
        buffer.write('{\n')
        ident_inner = ident+1
        for k,v in obj.items():
            buffer.write(prefix_blank*ident_inner)
            buffer.write(f'{k}: ')
            cls.vtype.pretty_print_obj(v, buffer, ident_inner)
            buffer.write(',\n')
        buffer.write(prefix_blank*ident)
        buffer.write('}')

    def to_json_serializable(cls, obj):
        amap = {}
        for k,v in obj.items():
            kk = Base.to_json_data(value_type=(k, cls.ktype))
            vv = Base.to_json_data(value_type=(v, cls.vtype))
            amap[kk] = vv
        return amap

