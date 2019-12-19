from canoser.base import Base
from canoser.int_type import Uint32, Uint8
import struct


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

