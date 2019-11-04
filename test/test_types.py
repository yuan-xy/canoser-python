from canoser import *
import pdb
import pytest

def test_str_to_int():
    with pytest.raises(Exception):
        Uint8.int_unsafe("")
    assert 0 == Uint8.int_unsafe("0")
    assert 0 == Uint8.int_unsafe(b"0")
    assert 1 == Uint8.int_unsafe(b"01")
    assert 0 == Uint8.int_unsafe("0"*100)
    assert 255 == Uint8.int_unsafe("255")
    assert 255 == Uint8.int_unsafe("0255")
    with pytest.raises(Exception):
        Uint8.int_unsafe("-1")
    with pytest.raises(Exception):
        Uint8.int_unsafe("256")

def test_str_to_int_strict():
    assert 0 == Uint8.int_safe(0)
    assert 255 == Uint8.int_safe(255)
    assert -128 == Int8.int_safe(-128)
    assert 127 == Int8.int_safe(127)
    assert 0 == Uint8.int_safe("0")
    assert 255 == Uint8.int_safe("255")
    assert -128 == Int8.int_safe("-128")
    assert 127 == Int8.int_safe("127")
    assert 65535 == Uint16.int_safe("65535")
    with pytest.raises(Exception):
        Uint8.int_safe("")
    with pytest.raises(Exception):
        Uint8.int_safe(b"0")
    with pytest.raises(Exception):
        Uint8.int_safe(b"01")
    with pytest.raises(Exception):
        Uint8.int_safe("0"*100)
    with pytest.raises(Exception):
        Uint8.int_safe("0255")
    with pytest.raises(Exception):
        Uint8.int_safe("-1")
    with pytest.raises(Exception):
        Uint8.int_safe("256")
    with pytest.raises(Exception):
        Int8.int_safe("-129")
    with pytest.raises(Exception):
        Int8.int_safe("128")
    with pytest.raises(Exception):
        Uint8.int_safe(-1)
    with pytest.raises(Exception):
        Uint8.int_safe(256)
    with pytest.raises(Exception):
        Int8.int_safe(-129)
    with pytest.raises(Exception):
        Int8.int_safe(128)

def test_bool_cast_int():
    assert isinstance(True, bool) == True
    assert isinstance(True, int) == True
    assert True == 1
    assert False == (True < 1)
    with pytest.raises(Exception):
        Int8.int_safe(True)
    with pytest.raises(Exception):
        Int8.int_safe(False)
    with pytest.raises(Exception):
        Int8.int_safe(None)

def test_int():
    assert Int8.encode(16) == Uint8.encode(16)


def test_uint8():
    assert Uint8.encode(16) == b"\x10"
    assert Uint8.decode_bytes(b"\x10") == 16
    assert Uint8.max_value == 255
    assert Uint8.min_value == 0

def test_uint8_illegal():
    with pytest.raises(Exception):
        Uint8.encode(-1)
    with pytest.raises(Exception):
        Uint8.encode(0.1)
    with pytest.raises(Exception):
        Uint8.encode([0])
    with pytest.raises(Exception):
        Uint8.encode(b'0')

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
    assert BytesT.pack(1,2,3) == bytes([1,2,3])

def test_array():
    arrt = ArrayT(Uint8, 2)
    assert arrt.encode([1, 2]) == b'\x02\x00\x00\x00\x01\x02'
    arr = arrt.decode(Cursor(b'\x02\x00\x00\x00\x01\x02'))
    assert arr == [1, 2]
    with pytest.raises(TypeError):
        arrt.decode(Cursor(b'\x01\x00\x00\x00\x01\x02'))
    with pytest.raises(TypeError):
        arrt.decode(Cursor(b'\x03\x00\x00\x00\x01\x02'))

def test_deserialize_int_array():
    arrt = ArrayT(BoolT, 2)
    bools = arrt.decode(Cursor([2,0,0,0,1,0]))
    assert bools == [True, False]

def test_tuple():
    tuplet = TupleT(StrT, Uint8, BoolT)
    assert tuplet.encode(("abc", 1, False)) == b'\x03\x00\x00\x00\x61\x62\x63\x01\x00'
    ret = tuplet.decode(Cursor(b'\x03\x00\x00\x00\x61\x62\x63\x01\x00'))
    assert ret == ("abc", 1, False)

