import pytest
import pdb
from canoser import *
from datetime import datetime

# Test Example in https://github.com/libra/libra/tree/master/common/canonical_serialization/README.md

ADDRESS_LENGTH = 32
ED25519_PUBLIC_KEY_LENGTH = 32
ED25519_SIGNATURE_LENGTH = 64


#pub struct ByteArray(Vec<u8>);

class TransactionArgument(RustEnum):
    _enums = [
        ('U64', Uint64),
        ('Address', [Uint8, ADDRESS_LENGTH]),
        ('String', str),
        ('ByteArray', [Uint8])
    ]

class WriteOp(RustEnum):
    _enums = [
        ('Deletion', None),
        ('Value', [Uint8])
    ]

class AccessPath(Struct):
    _fields = [
        ('address', [Uint8, ADDRESS_LENGTH]),
        ('path', [Uint8])
    ]


class Program(Struct):
    _fields = [
        ('code', [Uint8]),
        ('args', [TransactionArgument]),
        ('modules', [[Uint8]])
    ]


# `WriteSet` contains all access paths that one transaction modifies. Each of them is a `WriteOp`
# where `Value(val)` means that serialized representation should be updated to `val`, and
# `Deletion` means that we are going to delete this access path.
class WriteSet(Struct):
    _fields = [
        ('write_set', [(AccessPath, WriteOp)])
    ]


class Module(Struct):
    _fields = [
        ('code', [Uint8])
    ]


class Script(Struct):
    _fields = [
        ('code', [Uint8]),
        ('args', [TransactionArgument])
    ]

class TransactionPayload(RustEnum):
    _enums = [
        ('Program', Program),
        ('WriteSet', WriteSet),
        ('Script', Script),
        ('Module', Module)
    ]

class RawTransaction(Struct):
    _fields = [
        ('sender', [Uint8, ADDRESS_LENGTH]),
        ('sequence_number', Uint64),
        ('payload', TransactionPayload),
        ('max_gas_amount', Uint64),
        ('gas_unit_price', Uint64),
        ('expiration_time', Uint64)
    ]

 
def test_readme_example1():
	lcs = '0200000020000000A71D76FAA2D2D5C3224EC3D41DEB293973564A791E55C6782BA76C2BF0495F9A2100000001217DA6C6B3E19F1825CFB2676DAECCE3BF3DE03CF26647C78DF00B371B25CC970000000020000000C4C63F80C74B11263E421EBF8486A4E398D0DBC09FA7D4F62CCDB309F3AEA81F0900000001217DA6C6B3E19F180100000004000000CAFED00D'
	tx = WriteSet.deserialize(bytes.fromhex(lcs))
	print(tx)

def test_readme_example2():
	lcs = '00000000040000006D6F766502000000020000000900000043414645204430304402000000090000006361666520643030640300000001000000CA02000000FED0010000000D'
	tx = TransactionPayload.deserialize(bytes.fromhex(lcs))
	print(tx)

def test_readme_example3():
	lcs = '010000000200000020000000A71D76FAA2D2D5C3224EC3D41DEB293973564A791E55C6782BA76C2BF0495F9A2100000001217DA6C6B3E19F1825CFB2676DAECCE3BF3DE03CF26647C78DF00B371B25CC970000000020000000C4C63F80C74B11263E421EBF8486A4E398D0DBC09FA7D4F62CCDB309F3AEA81F0900000001217DA6C6B3E19F180100000004000000CAFED00D'
	tx = TransactionPayload.deserialize(bytes.fromhex(lcs))
	print(tx)

def test_readme_example4():
	lcs = '200000003A24A61E05D129CACE9E0EFC8BC9E33831FEC9A9BE66F50FD352A2638A49B9EE200000000000000000000000040000006D6F766502000000020000000900000043414645204430304402000000090000006361666520643030640300000001000000CA02000000FED0010000000D1027000000000000204E0000000000008051010000000000'
	tx = RawTransaction.deserialize(bytes.fromhex(lcs))
	print(tx)
	

def test_readme_example5():
	lcs = '20000000C3398A599A6F3B9F30B635AF29F2BA046D3A752C26E9D0647B9647D1F4C04AD42000000000000000010000000200000020000000A71D76FAA2D2D5C3224EC3D41DEB293973564A791E55C6782BA76C2BF0495F9A2100000001217DA6C6B3E19F1825CFB2676DAECCE3BF3DE03CF26647C78DF00B371B25CC970000000020000000C4C63F80C74B11263E421EBF8486A4E398D0DBC09FA7D4F62CCDB309F3AEA81F0900000001217DA6C6B3E19F180100000004000000CAFED00D00000000000000000000000000000000FFFFFFFFFFFFFFFF'
	tx = RawTransaction.deserialize(bytes.fromhex(lcs))
	print(tx)
