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

First define a data structure with Canoser, that is, write a class that inherits from "Canoser::Struct", and then define the fields owned by the structure through the "define_field" method. This structure naturally has the ability to canonical serialize and deserialize types. For example, the following AccountResource defines a data structure of the same name in the Libra code：
```python
  #python code，define canoser data structure
  class AccountResource < Canoser::Struct
  	define_field :authentication_key, [Canoser::Uint8]
  	define_field :balance, Canoser::Uint64
  	define_field :delegated_withdrawal_capability, Canoser::Bool
  	define_field :received_events_count, Canoser::Uint64
  	define_field :sent_events_count, Canoser::Uint64
  	define_field :sequence_number, Canoser::Uint64
  end
```

Here is the code that defines this data structure and serialization in Libra code:
```rust
// rust code in Libra
// define the data structure
pub struct AccountResource {
    balance: u64,
    sequence_number: u64,
    authentication_key: ByteArray,
    sent_events_count: u64,
    received_events_count: u64,
    delegated_withdrawal_capability: bool,
}
// serialization
impl CanonicalSerialize for AccountResource {
    fn serialize(&self, serializer: &mut impl CanonicalSerializer) -> Result<()> {
        serializer
            .encode_struct(&self.authentication_key)?
            .encode_u64(self.balance)?
            .encode_bool(self.delegated_withdrawal_capability)?
            .encode_u64(self.received_events_count)?
            .encode_u64(self.sent_events_count)?
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
| Canoser::Uint8 |  | Unsigned 8-bit integer |
| Canoser::Uint16 |  | Unsigned 16-bit integer|
| Canoser::Uint32 |  | Unsigned 32-bit integer |
| Canoser::Uint64 |  | Unsigned 64-bit integer |
| Canoser::Int8 |  | Signed 8-bit integer |
| Canoser::Int16 |  | Signed 16-bit integer|
| Canoser::Int32 |  | Signed 32-bit integer |
| Canoser::Int64 |  | Signed 64-bit integer |
| Canoser::Bool |  | Boolean |
| Canoser::Str |  | String |
| [] | supported | Array Type |
| {} | supported |  Map Type |
| A Canoser::Struct Name|  | Another structure nested (cannot be recycled) |

### About Array Type
The default data type (if not defined) in the array is Uint8. The following two definitions are equivalent:
```python
  class Arr1 < Canoser::Struct
    define_field :addr, []
  end
  class Arr2 < Canoser::Struct
    define_field :addr, [Canoser::Uint8]
  end  
```  
Arrays can also define lengths to represent fixed length data. For example, the address in Libra is 256 bits, which is 32 bytes, so it can be defined as follows:
```python
  class Address < Canoser::Struct
    define_field :addr, [Canoser::Uint8], 32
  end  
```  
When the fixed length data is serialized, the length information is not written to the output.


### About map type
The default data type (if not defined) in the map is an array of Uint8. The following two definitions are equivalent:
```python
  class Map1 < Canoser::Struct
    define_field :addr, {}
  end
  class Map2 < Canoser::Struct
    define_field :addr, {[Canoser::Uint8] => [Canoser::Uint8]}
  end  
```  

### Nested data structure
The following is a complex example with three data structures:
```python
  class Addr < Canoser::Struct
    define_field :addr, [Canoser::Uint8], 32
  end

  class Bar < Canoser::Struct
    define_field :a, Canoser::Uint64
    define_field :b, [Canoser::Uint8]
    define_field :c, Addr
    define_field :d, Canoser::Uint32
  end

  class Foo < Canoser::Struct
    define_field :a, Canoser::Uint64
    define_field :b, [Canoser::Uint8]
    define_field :c, Bar
    define_field :d, Canoser::Bool
    define_field :e, {}
  end
```
This example refers to the test code from canonical serialization in libra.

### Serialization and deserialization
After defining Canoser::Struct, you don't need to implement serialization and deserialization code yourself, you can directly call the default implementation of the base class. Take the AccountResource structure as an example:

```python
# serialize an object
obj = AccountResource.new(authentication_key:[...],...)
bytes = obj.serialize

# deserialize an object from bytes
obj = AccountResource.deserialize(bytes)
```

### Get field value from object 
For all fields defined by the "define_field" method, the value of this field of an object can be obtained via field_name. such as:

```python
obj.authentication_key
```


## Development

After checking out the repo, run `bin/setup` to install dependencies. Then, run `rake test` to run the tests. You can also run `bin/console` for an interactive prompt that will allow you to experiment.

To install this gem onto your local machine, run `bundle exec rake install`. To release a new version, update the version number in `version.rb`, and then run `bundle exec rake release`, which will create a git tag for the version, push git commits and tags, and push the `.gem` file to [pythongems.org](https://pythongems.org).

## Contributing

Bug reports and pull requests are welcome on GitHub at https://github.com/yuanxinyu/canoser. This project is intended to be a safe, welcoming space for collaboration, and contributors are expected to adhere to the [Contributor Covenant](http://contributor-covenant.org) code of conduct.

## License

The gem is available as open source under the terms of the [MIT License](https://opensource.org/licenses/MIT).

