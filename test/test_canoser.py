from canoser import *
import pdb

def test_int():
    assert Int8.encode(16) == Uint8.encode(16)


def test_uint8():
    assert Uint8.encode(16) == b"\x10"
    assert Uint8.decode_bytes(b"\x10") == 16
    assert Uint8.max_value() == 255


def test_int8():
    assert Int8.encode(16) == b"\x10"
    assert Int8.decode_bytes(b"\x10") == 16
    assert Int8.max_value() == 127
    assert Int8.encode(-1) ==  b"\xFF"
    #assert false == b"\xFF".valid_encoding?   #not a valid utf-8 sequence
    assert Int8.decode_bytes(b"\xFF") == -1
    assert Int8.decode_bytes(b"\x80") == -128


def test_uint16():
    assert Uint16.encode(16) == b"\x10\x00"
    assert Uint16.encode(257) == b"\x01\x01"
    assert Uint16.decode_bytes(b"\x01\x01") == 257


def test_uint32():
    assert Uint32.encode(16) == b"\x10\x00\x00\x00"
    assert Uint32.encode(0x12345678) == b"\x78\x56\x34\x12"
    assert Uint32.decode_bytes(b"\x78\x56\x34\x12") == 0x12345678


def test_uint64():
    assert Uint64.encode(16) == b"\x10\x00\x00\x00\x00\x00\x00\x00"
    assert Uint64.encode(0x1234567811223344) == b"\x44\x33\x22\x11\x78\x56\x34\x12" 
    assert Uint64.decode_bytes(b"\x44\x33\x22\x11\x78\x56\x34\x12" ) == 0x1234567811223344
