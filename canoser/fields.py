import struct


class IntType:
    _pack_map = {8: "B", 16: "H", 32: "L", 64: "Q"}

    def __init__(self, bits, signed=False):
        self.bits = bits
        self.signed = signed

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

    def max_value(self):
        if self.signed:
            return 2**(self.bits-1) - 1
        else:
            return 2**(self.bits) - 1


Int8 = IntType(8, True)
Int16 = IntType(16, True)
Int32 = IntType(32, True)
Int64 = IntType(64, True)

Uint8 = IntType(8)
Uint16 = IntType(16)
Uint32 = IntType(32)
Uint64 = IntType(64)

