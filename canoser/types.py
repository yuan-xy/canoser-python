import struct

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

    def check_value(self, value):
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


class ArrayT:

    def __init__(self, atype, fixed_len=None):
        self.atype = atype
        if fixed_len is not None and fixed_len <= 0:
            raise TypeError("arr len must > 0".format(fixed_len))
        self.fixed_len = fixed_len

    def encode(self, arr):
        output = b""
        output += Uint32.encode(len(arr))
        for item in arr:
            output += self.atype.encode(item)
        return output

    def decode(self, cursor):
        arr = []
        size = Uint32.decode(cursor)
        if self.fixed_len is not None:
            if size != self.fixed_len:
                raise TypeError(f"{size} is not equal to predefined value: {self.fixed_len}")
        for _ in range(size):
            arr.append(self.atype.decode(cursor))
        return arr

    def check_value(self, arr):
        if self.fixed_len is not None and len(arr) != self.fixed_len:
            raise TypeError("arr len not match: {}-{}".format(len(arr), self.fixed_len))
        for item in arr:
            self.atype.check_value(item)

    def __eq__(self, other):
        if not isinstance(other, ArrayT):
            return False
        return self.atype == other.atype


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
            kvs[k] = v
        return kvs

    def check_value(self, kvs):
        for k, v in kvs.items():
            self.ktype.check_value(k)
            self.vtype.check_value(v)

    def __eq__(self, other):
        if not isinstance(other, MapT):
            return False
        return self.ktype == other.ktype and self.vtype == other.vtype


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


class OptionalObj:
    def __init__(self, value=None):
        self.value = value


class OptionalT:
    def __init__(self, atype):
        self.atype = type_mapping(atype)

    def encode(self, optional):
        if optional.value is not None:
            ret = BoolT.encode(True)
            ret += self.atype.encode(optional.value)
            return ret
        else:
            return BoolT.encode(False)

    def decode(self, cursor):
        exist = BoolT.decode(cursor)
        if exist:
            value = self.atype.decode(cursor)
            return OptionalObj(value)
        else:
            return OptionalObj()

    def check_value(self, opt):
        if not isinstance(opt, OptionalObj):
            raise TypeError(f"{opt} is not instance of OptionalObj")
        if opt.value is not None:
            self.atype.check_value(opt.value)

    def __eq__(self, other):
        if not isinstance(other, OptionalT):
            return False
        return self.atype == other.atype




class EnumObj:
    def __init__(self, index, value=None):
        self.index = index
        self.value = value


class EnumT:
    def __init__(self, **kwargs):
        self.names = list(kwargs.keys())
        self.types = [type_mapping(t) for t in kwargs.values()]

    def encode(self, enum):
        ret = Uint32.encode(enum.index)
        if self.types[enum.index] is not None:
            ret += self.types[enum.index].encode(enum.value)
        return ret

    def decode(self, cursor):
        index = Uint32.decode(cursor)
        if self.types[index] is not None:
            value = self.types[index].decode(cursor)
            return EnumObj(index, value)
        else:
            return EnumObj(index)

    def check_value(self, enum):
        if not isinstance(enum, EnumObj):
            raise TypeError(f"{enum} is not instance of EnumObj")
        if enum.index < 0 or enum.index >= len(self.types):
            raise TypeError(f"{enum.index} out of range:[0, {len(self.types)})")
        if self.types[enum.index] is not None:
            self.types[enum.index].check_value(enum.value)

    def __eq__(self, other):
        if not isinstance(other, EnumT):
            return False
        return self.types == other.types


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
    else:
        return field_type