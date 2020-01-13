import struct
from canoser.int_type import Uint32
from canoser.base import Base

class BytesT(Base):
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
    def to_json_serializable(cls, obj):
        return obj.hex()


