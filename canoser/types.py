import struct
from canoser.base import Base

class IntType:
    _pack_map = {8: "B", 16: "H", 32: "L", 64: "Q"}

    def __init__(self, bits, signed=False):
        self.bits = bits
        self.signed = signed

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        if self.signed:
            return f"Int{self.bits}"
        else:
            return f"Uint{self.bits}"

    @classmethod
    def pretty_print_obj(cls, value, buffer, ident):
        buffer.write(f'{value}')

    def pack_str(self):
        endian = '<'
        pack = IntType._pack_map[self.bits]
        if self.signed:
            pack = pack.lower()
        return endian + pack

    def encode(self, value):
        return struct.pack(self.pack_str(), value)

    def decode_bytes(self, bytes):
        return struct.unpack(self.pack_str(), bytes)[0]

    def decode(self, cursor):
        bytes = cursor.read_bytes(int(self.bits / 8))
        return self.decode_bytes(bytes)

    @property
    def max_value(self):
        if self.signed:
            return 2**(self.bits - 1) - 1
        else:
            return 2**(self.bits) - 1

    @property
    def min_value(self):
        if self.signed:
            return -2**(self.bits - 1)
        else:
            return 0

    def int_unsafe(self, s):
        ret = int(s)
        self.check_value(ret)
        return ret

    def int_safe(self, s):
        if isinstance(s, bool):
            raise TypeError(f"{s} is not a integer")
        if isinstance(s, int):
            self.check_value(s)
            return s
        if not isinstance(s, str):
            raise TypeError(f"{s} is not instance of <str>.")
        if len(s) < 1:
            raise TypeError(f"'{s}' is empty.")
        len_min = len(str(self.min_value))
        len_max = len(str(self.max_value))
        if len(s) > max(len_min, len_max):
            raise TypeError(f"Length of {s} is larger than max:{max(len_min, len_max)}.")
        ret = int(s)
        self.check_value(ret)
        return ret

    def check_value(self, value):
        if not isinstance(value, int):
            raise TypeError(f"{value} is not instance of <int>.")
        min, max = self.min_value, self.max_value
        if value < min or value > max:
            raise TypeError('value {} not in range {}-{}'.format(value, min, max))


Int8 = IntType(8, True)
Int16 = IntType(16, True)
Int32 = IntType(32, True)
Int64 = IntType(64, True)

Uint8 = IntType(8)
Uint16 = IntType(16)
Uint32 = IntType(32)
Uint64 = IntType(64)


class StrT:
    @classmethod
    def encode(self, value):
        output = b''
        utf8 = value.encode('utf-8')
        output += Uint32.encode(len(utf8))
        output += utf8
        return output

    @classmethod
    def decode(self, cursor):
        strlen = Uint32.decode(cursor)
        return str(cursor.read_bytes(strlen), encoding='utf-8')

    @classmethod
    def check_value(self, value):
        if not isinstance(value, str):
            raise TypeError('value {} is not string'.format(value))

    @classmethod
    def pretty_print_obj(cls, value, buffer, ident):
        buffer.write(f'{value}')


class BytesT:
    @classmethod
    def pack(self, *uint8s):
        output = b''
        for uint8 in uint8s:
            output += struct.pack("<B", uint8)
        return output

    @classmethod
    def encode(self, value):
        output = b''
        output += Uint32.encode(len(value))
        output += value
        return output

    @classmethod
    def decode(self, cursor):
        strlen = Uint32.decode(cursor)
        return cursor.read_bytes(strlen)

    @classmethod
    def check_value(self, value):
        if not isinstance(value, bytes):
            raise TypeError('value {} is not bytes'.format(value))

    @classmethod
    def pretty_print_obj(cls, value, buffer, ident):
        buffer.write(f'{value}')

    @classmethod
    def to_json_serializable(cls, obj):
        return obj.hex()



class BoolT:
    @classmethod
    def encode(self, value):
        if value:
            return b'\1'
        else:
            return b'\0'

    @classmethod
    def decode_bytes(self, value):
        if value == b'\0':
            return False
        elif value == b'\1':
            return True
        else:
            raise TypeError("bool should be 0 or 1.")

    @classmethod
    def decode(self, cursor):
        value = cursor.read_bytes(1)
        return self.decode_bytes(value)

    @classmethod
    def check_value(self, value):
        if not isinstance(value, bool):
            raise TypeError('value {} is not bool'.format(value))

    @classmethod
    def pretty_print_obj(cls, value, buffer, ident):
        buffer.write(f'{value}')


class ArrayT:

    def __init__(self, atype, fixed_len=None, encode_len=True):
        self.atype = atype
        if fixed_len is not None and fixed_len <= 0:
            raise TypeError("arr len must > 0".format(fixed_len))
        if fixed_len is None and not encode_len:
            raise TypeError("variable length sequences must encode len.")
        self.fixed_len = fixed_len
        self.encode_len = encode_len

    def encode(self, arr):
        output = b""
        if self.encode_len:
            output += Uint32.encode(len(arr))
        for item in arr:
            output += self.atype.encode(item)
        return output

    def decode(self, cursor):
        arr = []
        if self.encode_len:
            size = Uint32.decode(cursor)
            if self.fixed_len is not None and size != self.fixed_len:
                 raise TypeError(f"{size} is not equal to predefined value: {self.fixed_len}")
        else:
            size = self.fixed_len
        for _ in range(size):
            arr.append(self.atype.decode(cursor))
        return arr

    def check_value(self, arr):
        if self.fixed_len is not None and len(arr) != self.fixed_len:
            raise TypeError("arr len not match: {}-{}".format(len(arr), self.fixed_len))
        if not isinstance(arr, list):
            raise TypeError(f"{arr} is not a list.")
        for item in arr:
            self.atype.check_value(item)

    def __eq__(self, other):
        if not isinstance(other, ArrayT):
            return False
        return self.atype == other.atype

    def pretty_print_obj(cls, obj, buffer, ident):
        if cls.atype == Uint8:
            hex = struct.pack("<{}B".format(len(obj)), *obj).hex()
            buffer.write(hex)
        else:
            prefix_blank = '  '
            buffer.write('[\n')
            ident_inner = ident+1
            for _, item in enumerate(obj):
                buffer.write(prefix_blank*ident_inner)
                cls.atype.pretty_print_obj(item, buffer, ident_inner)
                buffer.write(',\n')
            buffer.write(prefix_blank*ident)
            buffer.write(']')

    def to_json_serializable(cls, obj):
        if cls.atype == Uint8:
            return struct.pack("<{}B".format(len(obj)), *obj).hex()
        ret = []
        for _, item in enumerate(obj):
            data = Base.to_json_data(value_type=(item, cls.atype))
            ret.append(data)
        return ret

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

class TupleT:

    def __init__(self, *ttypes):
        self.ttypes = ttypes

    def encode(self, value):
        output = b""
        zipped = zip(self.ttypes, value)
        for k, v in zipped:
            output += k.encode(v)
        return output

    def decode(self, cursor):
        arr = []
        for k in self.ttypes:
            arr.append(k.decode(cursor))
        return tuple(arr)

    def check_value(self, value):
        if len(value) != len(self.ttypes):
            raise TypeError(f"{len(value)} is not equal to {len(self.ttypes)}")
        if not isinstance(value, tuple):
            raise TypeError(f"{value} is not a tuple.")
        zipped = zip(self.ttypes, value)
        for k, v in zipped:
            k.check_value(v)

    def __eq__(self, other):
        if not isinstance(other, TupleT):
            return False
        zipped = zip(self.ttypes, other.ttypes)
        for t1, t2 in zipped:
            if t1 != t2:
                return False
        return True

    def pretty_print_obj(cls, obj, buffer, ident):
        prefix_blank = '  '
        buffer.write('(\n')
        ident_inner = ident+1
        zipped = zip(cls.ttypes, obj)
        for k, v in zipped:
            buffer.write(prefix_blank*ident_inner)
            if issubclass(k, Base):
                buffer.write(f'{k.__name__} ')
            k.pretty_print_obj(v, buffer, ident_inner)
            buffer.write(',\n')
        buffer.write(prefix_blank*ident)
        buffer.write(')')

    def to_json_serializable(cls, obj):
        ret = []
        #https://stackoverflow.com/questions/15721363/preserve-python-tuples-with-json
        #If need to deserialize tuple back later, above link will help.
        zipped = zip(cls.ttypes, obj)
        for k, v in zipped:
            data = Base.to_json_data(value_type=(v, k))
            ret.append(data)
        return ret


def my_import(name):
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

def type_mapping(field_type):
    if field_type == str:
        return StrT
    elif field_type == bytes:
        return BytesT
    elif field_type == bool:
        return BoolT
    elif type(field_type) == list:
        if len(field_type) == 0:
            return ArrayT(Uint8)
        elif len(field_type) == 1:
            item = field_type[0]
            return ArrayT(type_mapping(item))
        elif len(field_type) == 2:
            item = field_type[0]
            size = field_type[1]
            return ArrayT(type_mapping(item), size)
        elif len(field_type) == 3:
            item = field_type[0]
            size = field_type[1]
            encode_len = field_type[2]
            return ArrayT(type_mapping(item), size, encode_len)
        else:
            raise TypeError("Array has one item type, no more.")
        raise AssertionError("unreacheable")
    elif type(field_type) == dict:
        if len(field_type) == 0:
            ktype = BytesT
            vtype = [Uint8]
        elif len(field_type) == 1:
            ktype = next(iter(field_type.keys()))
            vtype = next(iter(field_type.values()))
        else:
            raise TypeError("Map type has one item mapping key type to value type.")
        return MapT(type_mapping(ktype), type_mapping(vtype))
    elif type(field_type) == tuple:
        arr = []
        for item in field_type:
            arr.append(type_mapping(item))
        return TupleT(*arr)
    elif type(field_type) == str:
        return my_import(field_type)
    else:
        return field_type