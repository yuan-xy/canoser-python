from canoser import *
import pytest
import pdb

ADDRESS_LENGTH = 32

input = [
        0xca, 0x82, 0x0b, 0xf9, 0x30, 0x5e, 0xb9, 0x7d, 0x0d, 0x78, 0x4f, 0x71, 0xb3, 0x95, 0x54,
        0x57, 0xfb, 0xf6, 0x91, 0x1f, 0x53, 0x00, 0xce, 0xaa, 0x5d, 0x7e, 0x86, 0x21, 0x52, 0x9e,
        0xae, 0x19,
    ]

expected_output = [
        0xCA, 0x82, 0x0B, 0xF9, 0x30, 0x5E, 0xB9, 0x7D, 0x0D, 0x78, 0x4F,
        0x71, 0xB3, 0x95, 0x54, 0x57, 0xFB, 0xF6, 0x91, 0x1F, 0x53, 0x00, 0xCE, 0xAA, 0x5D, 0x7E,
        0x86, 0x21, 0x52, 0x9E, 0xAE, 0x19,
    ]


class Address1(DelegateT):
    delegate_type = [Uint8, ADDRESS_LENGTH]


class Address2(DelegateT):
    delegate_type = [Uint8, ADDRESS_LENGTH, False]


def test_enocde_len():
    expected_output0 = [32, 0, 0, 0] + expected_output
    actual_output = Address1.encode(input)
    assert bytes(expected_output0) == actual_output

def test_not_enocde_len():
    actual_output = Address2.encode(input)
    assert bytes(expected_output) == actual_output

class AddrStruct(Struct):
    _fields = [('map', {Address2: [str]})]

def test_int_list_as_dict_key():
    amap = {bytes(input): ['test']}
    addrs = AddrStruct(amap)
    ser = addrs.serialize()
    addr2 = AddrStruct.deserialize(ser)
    assert addrs.map == addr2.map