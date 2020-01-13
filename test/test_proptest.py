from hypothesis import given
import hypothesis.strategies as st
from canoser import Struct, Uint8, Uint64, Uint128, Int8, Int64, Int128


def encode_decode_is_same(vtype, value):
	byts = vtype.encode(value)
	value2 = vtype.decode_bytes(byts)
	assert value == value2


@given(st.integers())
def test_prop(x):
	if x >= Uint8.min_value and x <= Uint8.max_value:
		encode_decode_is_same(Uint8, x)
	if x >= Uint64.min_value and x <= Uint64.max_value:
		encode_decode_is_same(Uint64, x)
	if x >= Uint128.min_value and x <= Uint128.max_value:
		encode_decode_is_same(Uint128, x)
	if x >= Int8.min_value and x <= Int8.max_value:
		encode_decode_is_same(Int8, x)
	if x >= Int64.min_value and x <= Int64.max_value:
		encode_decode_is_same(Int64, x)
	if x >= Int128.min_value and x <= Int128.max_value:
		encode_decode_is_same(Int128, x)


class PropStruct(Struct):
    _fields = [('name', str), ('value', Int128), ('flag', bool)]

@given(st.text(), st.integers(), st.booleans())
def test_ser_deser(name, value, flag):
	t = PropStruct(name, value, flag)
	ser = t.serialize()
	t2 = PropStruct.deserialize(ser)
	assert t == t2
