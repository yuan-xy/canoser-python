import pytest
import pdb
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
        x = TransactionArgument(UU64=0)
    with pytest.raises(TypeError):
        x = TransactionArgument(U64=0, String="a")
    with pytest.raises(TypeError):
        class NotDefineEnum(RustEnum):
            pass
        x = NotDefineEnum(X=0)


def test_enum():
    t_arg = TransactionArgument(U64=2)
    assert t_arg.index == 0
    assert t_arg.value == 2
    assert t_arg.U64 == True
    assert t_arg.value_type == Uint64
    t_arg.value = 3
    assert t_arg.value == 3
    with pytest.raises(TypeError):
        t_arg.value = 'abc'
    with pytest.raises(TypeError):
        t_arg.index = 2
    arg2 = TransactionArgument(String='abc')
    assert arg2.index == 2
    assert arg2.value == 'abc'
    assert arg2.String == True
    assert arg2.U64 == False
    assert arg2.value_type == StrT
    assert arg2.__class__ == t_arg.__class__
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
    #pdb.set_trace()
    e1 = Enum1.new(0, [5])
    e2 = Enum1(opt2=None)
    assert Enum1.new(1, None) == Enum1(opt2=None)
    assert Enum1.encode(e1) == b'\x00\x00\x00\x00\x01\x00\x00\x00\x05'
    assert Enum1.encode(e2) == b'\x01\x00\x00\x00'
    obj = Enum1.decode(Cursor(b'\x00\x00\x00\x00\x01\x00\x00\x00\x05'))
    assert obj.index == 0
    assert obj.value == [5]
    obj = Enum1.decode(Cursor(b'\x01\x00\x00\x00'))
    assert obj.index == 1
    assert obj.value == None
