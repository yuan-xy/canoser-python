from canoser.int_type import Uint32
from canoser.base import Base

class StrT(Base):
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
    def to_json_serializable(cls, obj):
        return obj


