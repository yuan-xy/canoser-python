# Canoser [![Canoser](https://img.shields.io/pypi/v/canoser.svg)](https://pypi.org/project/canoser/) [![python](https://img.shields.io/pypi/pyversions/canoser.svg)](https://pypi.org/project/canoser/) [![Build Status](https://travis-ci.org/yuan-xy/canoser-python.svg?branch=master)](https://travis-ci.org/yuan-xy/canoser-python) [![MIT licensed](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)

[中文文档 Chinese document](/README-CN.md)

A python implementation of the canonical serialization for the Libra network.

Canonical serialization guarantees byte consistency when serializing an in-memory
data structure. It is useful for situations where two parties want to efficiently compare
data structures they independently maintain. It happens in consensus where
independent validators need to agree on the state they independently compute. A cryptographic
hash of the serialized data structure is what ultimately gets compared. In order for
this to work, the serialization of the same data structures must be identical when computed
by independent validators potentially running different implementations
of the same spec in different languages.

## Installation

Require python 3.6 or above installed.

```sh
$ python3 -m pip install canoser
```


## Usage

First define a data structure with Canoser, that is, write a class that inherits from "canoser.Struct", and then define the fields owned by the structure through the "\_fields" array. This structure naturally has the ability to canonical serialize and deserialize types. For example, the following AccountResource defines a data structure of the same name in the Libra code：
```python
  #python code，define canoser data structure
from canoser import Struct, Uint8, Uint64
class AccountResource(Struct):
    _fields = [
        ('authentication_key', [Uint8]),
        ('balance', Uint64),
        ('delegated_withdrawal_capability', bool),
        ('received_events', EventHandle),
        ('sent_events', EventHandle),
        ('sequence_number', Uint64)
    ]
```

Here is the code that defines this data structure and serialization in Libra code:
```rust
// rust code in Libra
// define the data structure
pub struct AccountResource {
    balance: u64,
    sequence_number: u64,
    authentication_key: ByteArray,
    sent_events: EventHandle,
    received_events: EventHandle,
    delegated_withdrawal_capability: bool,
}
// serialization
impl CanonicalSerialize for AccountResource {
    fn serialize(&self, serializer: &mut impl CanonicalSerializer) -> Result<()> {
        serializer
            .encode_struct(&self.authentication_key)?
            .encode_u64(self.balance)?
            .encode_bool(self.delegated_withdrawal_capability)?
            .encode_struct(self.received_events)?
            .encode_struct(self.sent_events)?
            .encode_u64(self.sequence_number)?;
        Ok(())
    }
}
```
~~In the rust language used by Libra, it is necessary to manually write code to serialize/deserialize the data structure, and the order of the fields in the data structure and the order of serialization are not necessarily the same.~~

In Canoser, after defining the data structure, you don't need to write code to implement serialization and deserialization. Note that the order of the data structures in Canoser is defined in the order in which they are serialized in Libra.

### Supported field types

| field type | optionl sub type | description |
| ------ | ------ | ------ |
| canoser.Uint8 |  | Unsigned 8-bit integer |
| canoser.Uint16 |  | Unsigned 16-bit integer|
| canoser.Uint32 |  | Unsigned 32-bit integer |
| canoser.Uint64 |  | Unsigned 64-bit integer |
| canoser.Uint128 |  | Unsigned 128-bit integer |
| canoser.Int8 |  | Signed 8-bit integer |
| canoser.Int16 |  | Signed 16-bit integer|
| canoser.Int32 |  | Signed 32-bit integer |
| canoser.Int64 |  | Signed 64-bit integer |
| canoser.Int128 |  | Signed 128-bit integer |
| bool |  | Boolean |
| str |  | String |
| bytes |  | Binary String |
| [] | supported | Array Type |
| {} | supported |  Map Type |
| () | supported |  Tuple Type |
| canoser.Struct |  | Another structure nested (cannot be recycled) |
| RustEnum |  | Enum type |
| RustOptional |  | Optional type |

### About Array Type
The default data type (if not defined) in the array is Uint8. The following two definitions are equivalent:
```python
  class Arr1(Struct):
      _fields = [(addr, [])]


  class Arr2(Struct):
      _fields = [(addr, [Uint8])]

```
Arrays can also define lengths to represent fixed length data. For example, the address in Libra is 256 bits, which is 32 bytes, so it can be defined as follows:
```python
  class Address(Struct):
      _fields = [(addr, [Uint8, 32])]
```
When the fixed length data is serialized, you can skip the length information written to the output. For example, following code will generate 32 bytes without writing the length of the addr during serialization.

```python
  class Address(Struct):
      _fields = [(addr, [Uint8, 32, False])]
```


### About map type
The default data type (if not defined) in the map is an array of Uint8 in Libra, both of key and value.
But the python language dosn't support the array data type to be the key of a dict, so we change the key type from array of Uint8 to bytes in python, the type of value is unchanged.
The following two definitions are equivalent:
```python
  class Map1(Struct):
    _fields = [(addr, {})]


  class Map2(Struct):
    _fields = [(addr, {bytes : [Uint8] })]

```

### About enum type
In python and C, enum is just enumerated constants. But in Libra(Rust), a enum has a type constant and a optional Value. A rust enumeration is typically represented as:

```
enum SomeDataType {
  type0(u32),
  type1(u64),
  type2
}
```

To define a enum with Canoser, first write a class that inherits from "canoser.RustEnum", and then define the types owned by the enum through the "\_enums" array.
For example, the following TransactionArgument defines a data structure of the same name in the Libra code. The argument of a transaction can be one of the four types: Uint64 or Address or String or IntArray.：

```python
class TransactionArgument(RustEnum):
    _enums = [
        ('U64', Uint64),
        ('Address', [Uint8, ADDRESS_LENGTH]),
        ('String', str),
        ('ByteArray', [Uint8])
    ]
```
You can instantiate an enum obj and call its method and properties like this:

```python
    arg2 = TransactionArgument('String', 'abc')
    assert arg2.index == 2
    assert arg2.value == 'abc'
    assert arg2.String == True
    assert arg2.U64 == False
```

Every RustEnum object has an `index` property and a `value` property. After instantiated, the `index` can't be modified. You can only modify the `value` of an enum with correct data type.

For example, the following code is valid:

```python
    arg2 = TransactionArgument('String', 'abc')
    arg2.value == 'Bcd'
```

For example, the following code is invalid:
```python
    arg2.index = 0      #raise an exception
    arg2.value = [3]    #raise an exception
```

The RustEnum can have a enum without value type, which represented by `None`.

```python
class Enum1(RustEnum):
    _enums = [('opt1', [Uint8]), ('opt2', None)]

e2 = Enum1('opt2', None)
#or
e2 = Enum1('opt2')
```

You can also instantiate a RustEnum object by index and value.

```python
e1 = Enum1.new(0, [5])
# which is equivalent to
e1 = Enum1('opt1', [5])
```

### About optional type
An optional type in libra is a nullable data either exists in its full representation or does not. For example,

```
optional_data: Option(uint8); // Rust/Libra
uint8 *optional_data; // C
```
It has similar semantics meaning with the following enum type:
```
enum Option<uint8> {
    Some(uint8),
    None,
}
```

To define a optional with Canoser, first write a class that inherits from "canoser.RustOptional", and then define the types owned by RustOptional through the "\_type" field. For example,

```python
class OptionUInt(RustOptional):
    _type = Uint8

null = OptionUInt(None)
obj = OptionUInt(8)
assert obj.value == 8
```

Here's a complete example:

```python
class OptionStr(RustOptional):
    _type = str

class OptionTest(Struct):
    _fields = [
        ('message', OptionStr)
    ]

    def __init__(self, msg=None):
        if msg is not None:
            self.message = OptionStr(msg)
        else:
            self.message = OptionStr(None)

test = OptionTest('test_str')
assert test.message.value == 'test_str'
```


The RustOptional type in canoser is similar to `typing.Optional` in python. Note that this is not the same concept as an optional argument, which is one that has a default.


### Nested data structure
The following is a complex example with three data structures:
```python
class Addr(Struct):
    _fields = [('addr', [Uint8, 32])]


class Bar(Struct):
    _fields = [
        ('a', Uint64),
        ('b', [Uint8]),
        ('c', Addr),
        ('d', Uint32),
    ]

class Foo(Struct):
    _fields = [
        ('a', Uint64),
        ('b', [Uint8]),
        ('c', Bar),
        ('d', bool),
        ('e', {}),
    ]
```
This example refers to the test code from canonical serialization in libra.


### Serialization and deserialization
After defining canoser.Struct, you don't need to implement serialization and deserialization code yourself, you can directly call the default implementation of the base class. Take the AccountResource structure as an example:

```python
# serialize an object
obj = AccountResource(authentication_key=...,...)
bbytes = obj.serialize()

# deserialize an object from bytes
obj = AccountResource.deserialize(bbytes)
```

### Json pretty print

For any canoser `Struct`, you can call the `to_json` method to get a formatted json string:

```python
# serialize an object
print(obj.to_json())

```

### Get field value from object

For all fields defined by the "\_fields", the value of this field of an object can be obtained via field_name. such as:
```python
obj.authentication_key
```


## Rust Type Alias
For simple type alias in rust, such as:
```rust
// in rust
pub type Round = u64;
```

We can define the alias like this:

```python
# in python
Round = Uint64
```


## Rust Tuple Struct

Struct like Address and ByteArray has no fields:

```rust
pub struct Address([u8; ADDRESS_LENGTH]);
pub struct ByteArray(Vec<u8>);
```

These struct called `tuple struct` in `Rust` programming language. Tuple struct is like `typedef` other than struct in `C` like programming languages.

You can just define them as a direct type, no struct. Just code like this:
```python
class TransactionArgument(RustEnum):
    _enums = [
        ...
        ('Address', [Uint8, ADDRESS_LENGTH]),
        ...
    ]
```

Or you can define an `Address` class which inherit from `canoser.DelegateT` and has a `delegate_type` field with type `[Uint8, ADDRESS_LENGTH]`:

```python
class Address(DelegateT):
    delegate_type = [Uint8, ADDRESS_LENGTH]


class TransactionArgument(RustEnum):
    _enums = [
        ...
        ('Address', Address),
        ...
    ]
```

Do not instantiate a `canoser.DelegateT` type in assaignment, for example:

```python
transactionArgument.address = [...] #ok
transactionArgument.address = Address([...])  #error
```


## Notice

### Must define canoser struct by serialized fields and sequence, not the definition in the rust struct.

For example, the SignedTransaction in Libra is defined as following code:

```rust
pub struct SignedTransaction {
    raw_txn: RawTransaction,
    public_key: Ed25519PublicKey,
    signature: Ed25519Signature,
    transaction_length: usize,
}
```
But field `transaction_length` doesn't write to the output.

```rust
impl CanonicalSerialize for SignedTransaction {
    fn serialize(&self, serializer: &mut impl CanonicalSerializer) -> Result<()> {
        serializer
            .encode_struct(&self.raw_txn)?
            .encode_bytes(&self.public_key.to_bytes())?
            .encode_bytes(&self.signature.to_bytes())?;
        Ok(())
    }
}
```

So we define SignedTransaction in canoser as following code:
```python
class SignedTransaction(canoser.Struct):
    _fields = [
        ('raw_txn', RawTransaction),
        ('public_key', [Uint8, ED25519_PUBLIC_KEY_LENGTH]),
        ('signature', [Uint8, ED25519_SIGNATURE_LENGTH])
    ]
```

Here is another example. The definition sequence and serialize sequence is opposite in  `WriteOp`

```rust
pub enum WriteOp {
    Value(Vec<u8>),
    Deletion,
}

enum WriteOpType {
    Deletion = 0,
    Value = 1,
}

impl CanonicalSerialize for WriteOp {
    fn serialize(&self, serializer: &mut impl CanonicalSerializer) -> Result<()> {
        match self {
            WriteOp::Deletion => serializer.encode_u32(WriteOpType::Deletion as u32)?,
            WriteOp::Value(value) => {
                serializer.encode_u32(WriteOpType::Value as u32)?;
                serializer.encode_vec(value)?
            }
        };
        Ok(())
    }
}
```

So, we define `WriteOp` as follow:
```python
class WriteOp(RustEnum):
    _enums = [
        ('Deletion', None),
        ('Value', [Uint8])
    ]

```

## Related Projects

[MoveOnLibra OpenAPI: make writing libra wallet & move program easier](https://www.MoveOnLibra.com)

[A Ruby implementation of the LCS(Libra Canonical Serialization)](https://github.com/yuan-xy/canoser-ruby)

[A Python implementation of client APIs and command-line tools for the Libra network](https://github.com/yuan-xy/libra-client)



## License

The package is available as open source under the terms of the [MIT License](https://opensource.org/licenses/MIT).

