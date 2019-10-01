from canoser import *
import struct
import pdb
import pytest

ADDRESS_LENGTH = 32

class Address(DelegateT):
    delegate_type = [Uint8, ADDRESS_LENGTH]

    @classmethod
    def _pretty_print_obj(cls, obj, concat, ident):
        pdb.set_trace()
        hex = struct.pack("<{}B".format(len(obj)), *obj).hex()
        concat.write(hex)


class AddrStruct(Struct):
    _fields = [('addr', Address)]

def test_array():
    with pytest.raises(TypeError):
        x = AddrStruct([1,2,3])
    arr = []
    for _ in range(ADDRESS_LENGTH):
        arr.append(5)
    x = AddrStruct(arr)
    sx = x.serialize()
    x2 = AddrStruct.deserialize(sx)
    assert x.addr == x2.addr
