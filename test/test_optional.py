import pytest
import pdb
from canoser import *

class OptionUInt(RustOptional):
    _type = Uint8

def test_optional():
    null = OptionUInt(None)
    obj = OptionUInt(8)
    assert OptionUInt.encode(null) == b'\x00'
    assert OptionUInt.encode(obj) == b'\x01\x08'
    assert OptionUInt.decode(Cursor(b'\x01\x08')).value == 8
    assert OptionUInt.decode(Cursor(b'\x00')).value == None
    assert obj.serialize() == b'\x01\x08'
    assert obj == OptionUInt.deserialize(obj.serialize())
    with pytest.raises(TypeError):
        obj.value = -1
    with pytest.raises(TypeError):
        obj.value = "abc"
    obj.value = None
    assert obj.value == None
    obj.value = 123
    assert obj.value == 123


class OptionInt(RustOptional):
    _type = Int8

class OStruct(Struct):
    _fields = [('opt', OptionInt)]

def test_optional_struct():
    x = OStruct(opt = OptionInt(-1))
    assert OStruct.opt.expected_type == OptionInt
    sx = x.serialize()
    assert sx == b'\x01\xff'
    x2 = OStruct.deserialize(sx)
    assert x.opt.value == x2.opt.value
    with pytest.raises(TypeError):
        x.opt = -1

def test_optional_struct_null():
    x = OStruct(opt = OptionInt())
    assert x.opt.value is None
    sx = x.serialize()
    assert sx == b'\x00'
    x2 = OStruct.deserialize(sx)
    assert x2.opt.value is None
