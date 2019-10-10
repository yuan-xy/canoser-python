from canoser import *
import struct
import pdb
import pytest

ADDRESS_LENGTH = 32

class Address(DelegateT):
    delegate_type = [Uint8, ADDRESS_LENGTH]

    @classmethod
    def pretty_print_obj(cls, obj, concat, ident):
        hex = struct.pack("<{}B".format(len(obj)), *obj).hex()
        concat.write(f'"{hex}"')


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
    print(x2)
    assert x2.__str__() == """{
  addr: "0505050505050505050505050505050505050505050505050505050505050505",
}"""
    assert AddrStruct.addr.expected_type.dtype().atype == Uint8
    assert AddrStruct.addr.expected_type.dtype().fixed_len == ADDRESS_LENGTH

