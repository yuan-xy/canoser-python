import pytest
import pdb
from canoser import *


class Stock(Struct):
    _fields = [('name', str), ('shares', Uint8)]


def test_struct_init():
    s1 = Stock('ACME', 50)
    assert s1.name == "ACME"
    assert s1.shares == 50
    s2 = Stock('ACME', shares=50)
    s3 = Stock(name='ACME', shares=50)
    s6 = Stock(shares=50)
    with pytest.raises(TypeError):
        s4 = Stock('ACME', 500)
    with pytest.raises(TypeError):
        s5 = Stock('ACME', shares=50, aa=1)
    with pytest.raises(TypeError):
        s6 = Stock(123)


def test_struct_serialize():
    s1 = Stock('ACME', 50)
    bstr = s1.serialize()
    s2 = Stock.deserialize(bstr)
    assert s2.name == "ACME"
    assert s2.shares == 50

class BoolS(Struct):
    _fields = [('boolean', bool)]

def test_bool():
    x = BoolS(True)
    sx = x.serialize()
    x2 = BoolS.deserialize(sx)
    assert x.boolean == x2.boolean
    assert x.to_json() == """{
    "boolean": true
}"""

class ArrayS(Struct):
    _fields = [('array', [bool])]

def test_array():
    x = ArrayS([True, False, True])
    sx = x.serialize()
    assert b"\3\0\0\0\1\0\1" == sx
    x2 = ArrayS.deserialize(sx)
    assert x.array == x2.array

def test_array_error():
    with pytest.raises(TypeError):
        ArrayS.deserialize(b"\3\0\0\0\1\0\2")
    x = ArrayS([])
    with pytest.raises(TypeError):
        x.array = ["abc"]
    # with pytest.raises(TypeError):
    #     x.array.append("abc")


class ArrayUint8(Struct):
    _fields = [('array', [Uint8])]

def test_array():
    with pytest.raises(Exception):
        x = ArrayUint8([0.1])
    with pytest.raises(TypeError):
        x = ArrayUint8([-1])
    with pytest.raises(TypeError):
        x = ArrayUint8(b'')
    x = ArrayUint8([])
    with pytest.raises(TypeError):
        x.array = b''


class MapS(Struct):
    _fields = [('kvs', {str : Uint64})]

def test_map():
    x = MapS(kvs = {"count1":123456789, "count2":987654321})
    sx = x.serialize()
    x2 = MapS.deserialize(sx)
    assert x.kvs == x2.kvs

class ChineseMap(Struct):
    _fields = [('kvs', {str : str})]

def test_map2():
    x = ChineseMap(kvs = {"中文":"测试"})
    sx = x.serialize()
    x2 = ChineseMap.deserialize(sx)
    assert x.kvs == x2.kvs
    assert x2.kvs["中文"] == "测试"
    assert x2.to_json() == """{
    "kvs": {
        "\\u4e2d\\u6587": "\\u6d4b\\u8bd5"
    }
}"""



class ByteS(Struct):
    _fields = [('kvs', {bytes : Uint64})]

def test_bytes():
    x = ByteS(kvs = {b"count1":123456789, b"count2":987654321})
    sx = x.serialize()
    x2 = ByteS.deserialize(sx)
    assert x.kvs == x2.kvs
    with pytest.raises(TypeError):
        x2.kvs = {'a' : 'b'}
    print(x2.to_json())
    assert x2.to_json() == """{
    "kvs": {
        "636f756e7431": 123456789,
        "636f756e7432": 987654321
    }
}"""


class TupleS(Struct):
    _fields = [('tp', (str, Uint8, bool, Int16))]

def test_tuple_struct():
    x = TupleS(tp = ("abc", 1, False, 2))
    assert TupleS.tp.expected_type == TupleT(StrT, Uint8, BoolT, Int16)
    sx = x.serialize()
    assert sx == b'\x03\x00\x00\x00\x61\x62\x63\x01\x00\x02\x00'
    x2 = TupleS.deserialize(sx)
    assert x.tp == x2.tp
    with pytest.raises(TypeError):
        x.tp = ()
