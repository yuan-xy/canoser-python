import pytest
import pdb
from canoser import *


#copy form libra source code
TEST_VECTOR_1 = [
        0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x06, 0x64, 0x63, 0x58, 0x4d, 0x42, 0x37,
        0x64, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x09, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05,
        0x06, 0x07, 0x08, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05,
        0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05,
        0x05, 0x05, 0x05, 0x05, 0x05, 0x63, 0x00, 0x00, 0x00, 0x01, 0x03, 0x01, 0x01, 0x03, 0x16,
        0x15, 0x43, 0x03, 0x00, 0x38, 0x15, 0x03, 0x16, 0x0a, 0x05, 0x04, 0x14, 0x15, 0x59, 0x69,
        0x03, 0xc9, 0x17, 0x5a,
    ]

class Addr(Struct):
    _fields = [('addr', [Uint8, 32, False])]


class Bar(Struct):
    _fields = [
        ('a', Uint64),
        ('b', [Uint8]),
        ('c', Addr),
        ('d', Uint32),
    ]

class Foo(Struct):
    _fields = [
        ('a', Uint64),
        ('b', [Uint8]),
        ('c', Bar),
        ('d', bool),
        ('e', {}),
    ]


def test_with_libra_case():
    arr = []
    for _ in range(32):
    	arr.append(5)
    addr = Addr(addr=arr)
    bar = Bar(
        a = 100,
        b = [0, 1, 2, 3, 4, 5, 6, 7, 8],
        c = addr,
        d = 99
    )
    assert Bar.a.expected_type == Uint64
    assert Bar.b.expected_type == ArrayT(Uint8)
    assert Bar.c.expected_type == Addr
    assert Bar.d.expected_type == Uint32
    kvs = {}
    kvs[bytes([0, 56, 21])] = [22, 10, 5]
    kvs[bytes([1])] = [22, 21, 67]
    kvs[bytes([20, 21, 89, 105])] = [201, 23, 90]
    foo = Foo(
        a = Uint64.max_value,
        b = [100, 99, 88, 77, 66, 55],
        c = bar,
        d = True,
        e = kvs
    )
    str1 = foo.serialize()
    str2 = bytes(TEST_VECTOR_1)
    assert str1 == str2
    foo2 = Foo.deserialize(str1)
    assert foo == foo2
