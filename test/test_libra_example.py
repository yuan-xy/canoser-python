import pytest
import pdb
from canoser import *


#copy form libra source code
TEST_VECTOR_1 = "ffffffffffffffff060000006463584d4237640000000000000009000000000102\
                 03040506070820000000050505050505050505050505050505050505050505050505\
                 05050505050505056300000001030000000100000001030000001615430300000000\
                 381503000000160a05040000001415596903000000c9175a"

class Addr(Struct):
    _fields = [('addr', [Uint8, 32])]


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
    kvs[BytesT.pack(0, 56, 21)] = [22, 10, 5]
    kvs[BytesT.pack(1)] = [22, 21, 67]
    kvs[BytesT.pack(20, 21, 89, 105)] = [201, 23, 90]
    foo = Foo(
        a = Uint64.max_value,
        b = [100, 99, 88, 77, 66, 55],
        c = bar,
        d = True,
        e = kvs
    )
    str1 = foo.serialize()
    str2 = bytes.fromhex(TEST_VECTOR_1)
    assert str1 == str2
    foo2 = Foo.deserialize(str1)
    assert foo == foo2
