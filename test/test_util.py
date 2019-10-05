from canoser.util import *
import pdb

def int_list_to_bytes_v2(ints):
    return struct.pack("<{}B".format(len(ints)), *ints)

def test_address():
    hex_a = "000000000000000000000000000000000000000000000000000000000a550c18"
    int_a = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 85, 12, 24]
    bytes_a = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\nU\x0c\x18'
    assert hex_a.encode() == b"000000000000000000000000000000000000000000000000000000000a550c18"
    assert bytes.fromhex(hex_a) == bytes_a
    assert bytes(int_a) == bytes_a
    assert int_list_to_hex(int_a) == hex_a
    assert bytes_a.hex() == hex_a
    assert bytes_to_int_list(bytes_a) == int_a
    assert hex_to_int_list(hex_a) == int_a
    assert int_list_to_bytes_v2(int_a) == int_list_to_bytes(int_a)