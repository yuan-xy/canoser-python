from canoser import *
import struct
import pdb
import pytest

ADDRESS_LENGTH = 32

class Address(DelegateT):
    delegate_type = [Uint8, ADDRESS_LENGTH]


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
  "addr": "0505050505050505050505050505050505050505050505050505050505050505"
}"""
    assert AddrStruct.addr.expected_type.dtype().atype == Uint8
    assert AddrStruct.addr.expected_type.dtype().fixed_len == ADDRESS_LENGTH


class Bools(DelegateT):
    delegate_type = [bool]

def test_delegate():
    x = [True, False, True]
    bs = Bools.encode(x)
    assert bs == b'\x03\x01\x00\x01'
    x2 = Bools.deserialize(bs)
    assert x == x2
