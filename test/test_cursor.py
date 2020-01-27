from canoser import *
import pytest
import pdb

def test_read():
    data = [1,2,3,4,5]
    cursor = Cursor(data)
    assert cursor.read_bytes(1) == b'\x01'
    assert cursor.offset == 1
    assert cursor.peek_bytes(3) == b'\x02\x03\x04'
    assert cursor.offset == 1
    assert cursor.read_bytes(2) == b'\x02\x03'
    assert cursor.offset == 3
    assert cursor.is_finished() == False
    assert cursor.read_to_end() == b'\x04\x05'
    assert cursor.is_finished() == True