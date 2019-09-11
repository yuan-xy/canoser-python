# Canoser

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

```sh
$ pip install canoser
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
In the rust language used by Libra, it is necessary to manually write code to serialize/deserialize the data structure, and the order of the fields in the data structure and the order of serialization are not necessarily the same.

In Canoser, after defining the data structure, you don't need to write code to implement serialization and deserialization. Note that the order of the data structures in Canoser is defined in the order in which they are serialized in Libra.

### Supported field types

| field type | optionl sub type | description |
| ------ | ------ | ------ |
| canoser.Uint8 |  | Unsigned 8-bit integer |
| canoser.Uint16 |  | Unsigned 16-bit integer|
| canoser.Uint32 |  | Unsigned 32-bit integer |
| canoser.Uint64 |  | Unsigned 64-bit integer |
| canoser.Int8 |  | Signed 8-bit integer |
| canoser.Int16 |  | Signed 16-bit integer|
| canoser.Int32 |  | Signed 32-bit integer |
| canoser.Int64 |  | Signed 64-bit integer |
| bool |  | Boolean |
| str |  | String |
| bytes |  | Binary String |
| [] | supported | Array Type |
| {} | supported |  Map Type |
| A canoser.Struct |  | Another structure nested (cannot be recycled) |

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
When the fixed length data is serialized, the length information is not written to the output.


### About map type
The default data type (if not defined) in the map is an array of Uint8. The following two definitions are equivalent:
```python
  class Map1(Struct):
    _fields = [(addr, {})]


  class Map2(Struct):
    _fields = [(addr, {bytes : [Uint8] })]

```  

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
bbytes = obj.serialize

# deserialize an object from bytes
obj = AccountResource.deserialize(bbytes)
```

### Get field value from object 

For all fields defined by the "\_fields", the value of this field of an object can be obtained via field_name. such as:
```python
obj.authentication_key
```



## License

The package is available as open source under the terms of the [MIT License](https://opensource.org/licenses/MIT).

