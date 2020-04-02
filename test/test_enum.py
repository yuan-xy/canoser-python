import pytest
import pdb
from copy import copy, deepcopy
from canoser import *

ADDRESS_LENGTH = 32


class TransactionArgument(RustEnum):
    _enums = [
        ('U64', Uint64),
        ('Address', [Uint8, ADDRESS_LENGTH]),
        ('String', str),
        ('ByteArray', [Uint8])
    ]



def test_invalid():
    with pytest.raises(TypeError):
        t_arg = TransactionArgument()
    with pytest.raises(TypeError):
        x = TransactionArgument('UU64', 0)
    with pytest.raises(TypeError):
        class NotDefineEnum(RustEnum):
            pass
        x = NotDefineEnum('X')


def test_enum():
    t_arg = TransactionArgument('U64', 2)
    assert hasattr(t_arg, 'value')
    assert hasattr(t_arg, 'U64')
    assert hasattr(t_arg, 'Address')
    assert hasattr(t_arg, '__str__')
    assert hasattr(t_arg, 'to_proto') == False
    assert t_arg.index == 0
    assert t_arg.value == 2
    assert t_arg.U64 == True
    assert t_arg.enum_name == 'U64'
    assert t_arg.value_type == Uint64
    assert t_arg.serialize() == b"\x00\x02\x00\x00\x00\x00\x00\x00\x00"
    assert t_arg == TransactionArgument.deserialize(t_arg.serialize())
    t_arg.value = 3
    assert t_arg.value == 3
    with pytest.raises(TypeError):
        t_arg.value = 'abc'
    with pytest.raises(TypeError):
        t_arg.index = 2
    arg2 = TransactionArgument('String', 'abc')
    assert arg2.index == 2
    assert arg2.value == 'abc'
    assert arg2.String == True
    assert arg2.U64 == False
    assert arg2.value_type == StrT
    assert arg2.__class__ == t_arg.__class__
    arg2.value = 'Bcd'
    assert arg2.value == 'Bcd'
    with pytest.raises(TypeError):
        t_arg.value = 'abc'
    with pytest.raises(TypeError):
        arg2.value = 0
    with pytest.raises(TypeError):
        arg2.String = 0
    with pytest.raises(TypeError):
        arg2.String = 'abc'

class Enum1(RustEnum):
    _enums = [('opt1', [Uint8]), ('opt2', None)]


def test_enum2():
    e1 = Enum1.new_with_index_value(0, [5])
    e2 = Enum1('opt2', None)
    assert Enum1.new_with_index_value(1, None) == Enum1('opt2')
    assert Enum1.encode(e1) == b'\x00\x01\x05'
    assert Enum1.encode(e2) == b'\x01'
    obj = Enum1.decode(Cursor(b'\x00\x01\x05'))
    assert obj.index == 0
    assert obj.value == [5]
    obj = Enum1.decode(Cursor(b'\x01'))
    assert obj.index == 1
    assert obj.value == None

class Enum2(RustEnum):
    _enums = [('opt1', None), ('opt2', str)]


class EStruct(Struct):
    _fields = [('enum', Enum2)]

def test_enum_struct():
    EStruct.initailize_fields_type()
    assert EStruct.enum.expected_type == Enum2
    x = EStruct(Enum2('opt1'))
    sx = x.serialize()
    assert sx == b'\x00'
    x2 = EStruct.deserialize(sx)
    assert x.enum.index == x2.enum.index
    assert x.enum.value == x2.enum.value


class MyEnum(RustEnum):
    _enums = [('opt1', None), ('opt3', [[str]])]

class EStruct2(Struct):
    _fields = [('enum', MyEnum)]

def test_enum_struct2():
    EStruct2.initailize_fields_type()
    assert EStruct2.enum.expected_type == MyEnum
    x = EStruct2(MyEnum('opt3', [['ab', 'c'], ['d'], []]))
    deepcopy(x)
    sx = x.serialize()
    assert sx == b'\x01\x03' +\
        b'\x02' + b'\x02ab' + b'\x01c' +\
        b'\x01' + b'\x01d' + b'\x00'
    x2 = EStruct2.deserialize(sx)
    assert x.enum.index == x2.enum.index
    assert x.enum.value == x2.enum.value

class MyEnumWrap(MyEnum):
    pass

def test_enum_wrap():
    x1 = MyEnumWrap('opt1')
    x2 = MyEnumWrap('opt3', [['ab', 'c'], ['d'], []])
    assert x2.value == [['ab', 'c'], ['d'], []]
    assert x2.opt3 == True
    assert x2.opt1 == False
    x3 = copy(x2)
    x2.value = [['abc']]
    assert x2.opt3 == True
    assert x2.value == [['abc']]
    assert x3.value == [['ab', 'c'], ['d'], []]
    jstr = x3.to_json()
    print(jstr)
    assert x2.__repr__() == """MyEnumWrap{
  "opt3": [
    [
      "abc"
    ]
  ]
}"""
