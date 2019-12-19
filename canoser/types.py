import struct
from canoser.base import Base
from canoser.int_type import Uint8, Uint16, Uint32, Uint64, Int8, Int16, Int32, Int64
from canoser.tuple_t import TupleT
from canoser.map_t import MapT

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