import struct
from canoser.base import Base

class IntType(Base):

    @classmethod
    def to_json_serializable(cls, value):
        return value

    @classmethod
    def encode(cls, value):
        return struct.pack(cls.pack_str, value)

    @classmethod
    def decode_bytes(cls, bytes):
        return struct.unpack(cls.pack_str, bytes)[0]

    @classmethod
    def decode(cls, cursor):
        bytes = cursor.read_bytes(cls.byte_lens)
        return cls.decode_bytes(bytes)

    @classmethod
    def int_unsafe(cls, s):
        ret = int(s)
        cls.check_value(ret)
        return ret

    @classmethod
    def int_safe(cls, s):
        """
        Only allow safe str and valid int to be coerced to destination IntType
        """
        if isinstance(s, bool):
            raise TypeError(f"{s} is not a integer")
        if isinstance(s, int):
            cls.check_value(s)
            return s
        if not isinstance(s, str):
            raise TypeError(f"{s} is not instance of <str>.")
        if len(s) < 1:
            raise TypeError(f"'{s}' is empty.")
        len_min = len(str(cls.min_value))
        len_max = len(str(cls.max_value))
        if len(s) > max(len_min, len_max):
            raise TypeError(f"Length of {s} is larger than max:{max(len_min, len_max)}.")
        ret = int(s)
        cls.check_value(ret)
        return ret


    @classmethod
    def check_value(cls, value):
        if not isinstance(value, int):
            raise TypeError(f"{value} is not instance of <int>.")
        min, max = cls.min_value, cls.max_value
        if value < min or value > max:
            raise TypeError('value {} not in range {}-{}'.format(value, min, max))

class Int8(IntType):
    pack_str = "<b"
    byte_lens = 1
    max_value = 127
    min_value = -128

class Int16(IntType):
    pack_str = "<h"
    byte_lens = 2
    max_value = 32767
    min_value = -32768

class Int32(IntType):
    pack_str = "<l"
    byte_lens = 4
    max_value = 2147483647
    min_value = -2147483648

class Int64(IntType):
    pack_str = "<q"
    byte_lens = 8
    max_value = 9223372036854775807
    min_value = -9223372036854775808


class Uint8(IntType):
    pack_str = "<B"
    byte_lens = 1
    max_value = 255
    min_value = 0

class Uint16(IntType):
    pack_str = "<H"
    byte_lens = 2
    max_value = 65535
    min_value = 0

class Uint32(IntType):
    pack_str = "<L"
    byte_lens = 4
    max_value = 4294967295
    min_value = 0

class Uint64(IntType):
    pack_str = "<Q"
    byte_lens = 8
    max_value = 18446744073709551615
    min_value = 0


class Int128(IntType):
    byte_lens = 16
    max_value = 170141183460469231731687303715884105727
    min_value = -170141183460469231731687303715884105728

    @classmethod
    def encode(cls, value):
        return value.to_bytes(16, byteorder="little", signed=True)

    @classmethod
    def decode_bytes(cls, bytes):
        return int.from_bytes(bytes, byteorder='little', signed=True)



class Uint128(IntType):
    byte_lens = 16
    max_value = 340282366920938463463374607431768211455
    min_value = 0

    @classmethod
    def encode(cls, value):
        return value.to_bytes(16, byteorder="little", signed=False)

    @classmethod
    def decode_bytes(cls, bytes):
        return int.from_bytes(bytes, byteorder='little', signed=False)


