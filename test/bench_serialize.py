import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

import cProfile
from canoser import *
import pdb


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

def test_with_libra_case():
    for _i in range(10000):
        str1 = foo.serialize()
        foo2 = Foo.deserialize(str1)
        assert foo == foo2

cProfile.run('test_with_libra_case()', sort='cumtime')