import struct
import pdb

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

    def decode(self, cursor):
        bytes = cursor.read_bytes(int(self.bits/8))
        return self.decode_bytes(bytes)

    def max_value(self):
        if self.signed:
            return 2**(self.bits-1) - 1
        else:
            return 2**(self.bits) - 1

    def min_value(self):
        if self.signed:
            return -2**(self.bits-1)
        else:
            return 0


    def check_value(self, value):
    	min, max = self.min_value(), self.max_value()
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
