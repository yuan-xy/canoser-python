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

