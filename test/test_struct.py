import pytest
import pdb
from canoser import *

class Stock(Struct):
    _fields = [('name', str), ('shares', Uint8)]
    #_fields = ['name', 'shares']


def test_struct():
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
