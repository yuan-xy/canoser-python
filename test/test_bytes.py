from canoser import *
import pytest


ADDRESS_LENGTH = 32

input = b'\xca\x82\x0b\xf90^\xb9}\rxOq\xb3\x95TW\xfb\xf6\x91\x1fS\x00\xce\xaa]~\x86!R\x9e\xae\x19'

class Address1(DelegateT):
    delegate_type = BytesT(ADDRESS_LENGTH)


class Address2(DelegateT):
    delegate_type = BytesT(ADDRESS_LENGTH, encode_len=False)


def test_enocde_len():
    expected_output = bytes([32, 0, 0, 0]) + input
    actual_output = Address1.encode(input)
    assert expected_output == actual_output

def test_not_enocde_len():
    actual_output = Address2.encode(input)
    assert input == actual_output

class AddrStruct(Struct):
    _fields = [('map', {Address2: [str]})]

def test_address_as_dict_key():
    amap = {input: ['test']}
    addrs = AddrStruct(amap)
    ser = addrs.serialize()
    addr2 = AddrStruct.deserialize(ser)
    assert addrs.map == addr2.map