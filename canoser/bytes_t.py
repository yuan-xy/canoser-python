import struct
from canoser.int_type import Uint32
from canoser.base import Base

class BytesT(Base):

    def __init__(self, fixed_len=None, encode_len=True):
        if fixed_len is not None and fixed_len <= 0:
            raise TypeError("byte len must > 0".format(fixed_len))
        if fixed_len is None and not encode_len:
            raise TypeError("variable length sequences must encode len.")
        self.fixed_len = fixed_len
        self.encode_len = encode_len


    def encode(self, value):
        output = b""
        if self.encode_len:
            output += Uint32.encode(len(value))
        output += value
        return output


    def decode(self, cursor):
        if self.encode_len:
            size = Uint32.decode(cursor)
            if self.fixed_len is not None and size != self.fixed_len:
                 raise TypeError(f"{size} is not equal to predefined value: {self.fixed_len}")
        else:
            size = self.fixed_len
        return cursor.read_bytes(size)

    def check_value(self, value):
        if not isinstance(value, bytes):
            raise TypeError('value {} is not bytes'.format(value))
        if self.fixed_len is not None and len(value) != self.fixed_len:
            raise TypeError("len not match: {}-{}".format(len(value), self.fixed_len))


    def __eq__(self, other):
        if not isinstance(other, BytesT):
            return False
        return self.fixed_len == other.fixed_len and self.encode_len == other.encode_len


    def to_json_serializable(cls, obj):
        return obj.hex()


