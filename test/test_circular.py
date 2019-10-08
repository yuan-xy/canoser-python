from canoser import *
import pytest
import pdb

class Circular(Struct):
    _fields = [
        ('intv', Int8),
        ('next', ['test_circular.Circular'])
    ]

def test_circular():
    t1 = Circular(1,[])
    t2 = Circular(2,[])
    t12 = Circular(12,[t1, t2])
    bstr = t12.serialize()
    assert bstr == bytes([12]) + Uint32.encode(2) + t1.serialize() + t2.serialize()
    tt = Circular.deserialize(bstr)
    assert tt == t12
    assert Circular.deserialize(t1.serialize()) == t1
