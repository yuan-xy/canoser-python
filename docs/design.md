# Design of canoser

## Syntax
The basic principle of the syntax design is to use the python native syntax as many as possible. So, instead of define a type using canoser inner type class

```python
    _fields = [('an_array_of_boolean', canoser.ArrayT(canoser.BoolT))]
```
we support plain python array object:
```python
    _fields = [('an_array_of_boolean', [bool])]
```
`type_mapping` function is responsible to convert python object to canoser inner type.

we support plain python object in assignment statements as well:
```python
class Bar(Struct):
    _fields = [
        ('a', Uint64),
        ('b', [Uint8]),
        ('c', Addr),
        ('d', Uint32),
    ]
    bar = Bar(
        a = 100,
        b = [0, 1, 2, 3, 4, 5, 6, 7, 8],
        c = addr,
        d = 99
    )
```

## Canoser supported types

| field type syntax | canoser inner type | python object type |
| ------ | ------ | ------ |
| Uint8 | canoser.Uint8 | int |
| Uint16 | canoser.Uint16 | int |
| Uint32 | canoser.Uint32 | int |
| Uint64 | canoser.Uint64 | int |
| Uint128 | canoser.Uint128 | int |
| Int8 | canoser.Int8 | int |
| Int16 | canoser.Int16 | int |
| Int32 | canoser.Int32 | int |
| Int64 | canoser.Int64 | int |
| Int128 | canoser.Int128 | int |
| bool | BoolT | bool |
| str | StrT | str |
| bytes | BytesT | bytes |
| [] | ArrayT | list |
| {} | HashT |  dict |
| () | supported |  tuple |
| Struct | canoser.Struct | canoser.Struct |
| RustEnum | RustEnum | RustEnum |
| RustOptional | RustOptional | RustOptional |
| DelegateT | DelegateT | the object type of underline delegated type |

### Type and Object Separation
Because we choose to simplify the syntax of library users, so the implementation is a bitter complicated for canoser. For those types that python has support, such as int/bool/str/bytes/list/dict/tuple, the canoser type and the python type is diffrent of a canoser object.

### Canoser only Types
For those type that python language didn't has equivlent types, such as struct/enum/optional, we defined new class for them.


## Type interface

All types should implment four methods, such as:
```
    def encode(cls_or_obj, value)

    def decode(cls_or_obj, cursor)

    def check_value(cls_or_obj, value)

    #def _pretty_print_obj(cls_or_obj, obj, concat, ident) #deprecated, recommend json print

    def to_json_serializable(cls_or_obj, value)

```

`cls_or_obj` is either a canoser type class or a canoser type object. So those four methods can be classmethod or object method.

For example, `ArrayT(BoolT)` is type object, `BoolT` and `RustEnum` is type class.


## Type check
`check_value` is called when struct initailization or field assignment.

