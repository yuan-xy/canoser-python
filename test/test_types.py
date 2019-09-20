from canoser import *
import pdb
import pytest

def test_int():
    assert Int8.encode(16) == Uint8.encode(16)


def test_uint8():
    assert Uint8.encode(16) == b"\x10"
    assert Uint8.decode_bytes(b"\x10") == 16
    assert Uint8.max_value == 255
    assert Uint8.min_value == 0


def test_int8():
    assert Int8.encode(16) == b"\x10"
    assert Int8.decode_bytes(b"\x10") == 16
    assert Int8.max_value == 127
    assert Int8.min_value == -128
    assert Int8.encode(-1) ==  b"\xFF"
    assert Int8.decode_bytes(b"\xFF") == -1
    assert Int8.decode_bytes(b"\x80") == -128


def test_uint16():
    assert Uint16.encode(16) == b"\x10\x00"
    assert Uint16.encode(257) == b"\x01\x01"
    assert Uint16.decode_bytes(b"\x01\x01") == 257
    assert Uint16.max_value == 65535
    assert Uint16.min_value == 0

def test_int16():
    assert Int16.encode(16) == b"\x10\x00"
    assert Int16.decode_bytes(b"\x10\x00") == 16
    assert Int16.max_value == 32767
    assert Int16.min_value == -32768
    assert Int16.encode(-1) ==  b"\xFF\xFF"
    assert Int16.decode_bytes(b"\xFF\xFF") == -1
    assert Int16.decode_bytes(b"\x00\x80") == -32768

def test_uint32():
    assert Uint32.encode(16) == b"\x10\x00\x00\x00"
    assert Uint32.encode(0x12345678) == b"\x78\x56\x34\x12"
    assert Uint32.decode_bytes(b"\x78\x56\x34\x12") == 0x12345678


def test_uint64():
    assert Uint64.encode(16) == b"\x10\x00\x00\x00\x00\x00\x00\x00"
    assert Uint64.encode(0x1234567811223344) == b"\x44\x33\x22\x11\x78\x56\x34\x12"
    assert Uint64.decode_bytes(b"\x44\x33\x22\x11\x78\x56\x34\x12" ) == 0x1234567811223344

def test_bool():
    assert BoolT.encode(True) == b"\1"
    assert BoolT.encode(False) == b"\0"
    assert BoolT.decode_bytes(b"\1") == True
    assert BoolT.decode_bytes(b"\0") == False
    with pytest.raises(TypeError):
    	BoolT.decode_bytes("\x02")

def test_bytes():
    assert BytesT.pack(1,2,3) == BytesT.pack(*[1,2,3])

def test_array():
    arrt = ArrayT(Uint8, 2)
    assert arrt.encode([1, 2]) == b'\x02\x00\x00\x00\x01\x02'
    arr = arrt.decode(Cursor(b'\x02\x00\x00\x00\x01\x02'))
    assert arr == [1, 2]
    with pytest.raises(TypeError):
        arrt.decode(Cursor(b'\x01\x00\x00\x00\x01\x02'))
    with pytest.raises(TypeError):
        arrt.decode(Cursor(b'\x03\x00\x00\x00\x01\x02'))

def test_tuple():
    tuplet = TupleT(StrT, Uint8, BoolT)
    assert tuplet.encode(("abc", 1, False)) == b'\x03\x00\x00\x00\x61\x62\x63\x01\x00'
    ret = tuplet.decode(Cursor(b'\x03\x00\x00\x00\x61\x62\x63\x01\x00'))
    assert ret == ("abc", 1, False)

def test_optional():
    optional = OptionalT(Uint8)
    assert optional.encode(OptionalObj()) == b'\x00'
    assert optional.encode(OptionalObj(8)) == b'\x01\x08'
    assert optional.decode(Cursor(b'\x01\x08')).value == 8
    assert optional.decode(Cursor(b'\x00')).value == None

def test_enum():
    enumt = EnumT(opt1=Uint32, opt2=Uint16)
    assert enumt.names == ['opt1','opt2']
    assert enumt.opt1 == 0
    assert enumt.opt2 == 1
    assert enumt.encode(EnumObj(enumt.opt1, 5)) == b'\x00\x00\x00\x00\x05\x00\x00\x00'
    assert enumt.encode(EnumObj(1, 6)) == b'\x01\x00\x00\x00\x06\x00'
    obj = enumt.decode(Cursor(b'\x00\x00\x00\x00\x05\x00\x00\x00'))
    assert obj.index == 0
    assert obj.value == 5
    assert obj.index == enumt.opt1
    # assert obj.name == 'opt1'
    obj = enumt.decode(Cursor(b'\x01\x00\x00\x00\x06\x00'))
    assert obj.index == 1
    assert obj.value == 6
    assert obj.index == enumt.opt2

def test_enum2():
    enumt = EnumT(opt1=[Uint8], opt2=None)
    assert enumt.encode(EnumObj(0, [5])) == b'\x00\x00\x00\x00\x01\x00\x00\x00\x05'
    assert enumt.encode(EnumObj(enumt.opt2)) == b'\x01\x00\x00\x00'
    obj = enumt.decode(Cursor(b'\x00\x00\x00\x00\x01\x00\x00\x00\x05'))
    assert obj.index == 0
    assert obj.value == [5]
    obj = enumt.decode(Cursor(b'\x01\x00\x00\x00'))
    assert obj.index == 1
    assert obj.value == None
