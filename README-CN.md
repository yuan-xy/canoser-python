# Canoser


Canoser是facebook推出的Libra网络中使用的规范序列化LCS(Libra Canonical Serialization)协议的第三方python实现框架。

规范序列化可确保内存里的数据结构在序列化的时候保证字节一致性。它适用于双方想要有效比较他们独立维护的数据结构。在共识协议中，独立验证者需要就他们独立计算的状态达成一致。共识双方比较的是序列化数据的加密散列。要实现这一点，在计算时，相同数据结构的序列化必须相同。而独立验证器可能由不同的语言编写，有不同的实现代码，但是都遵循同一个规范。


## 安装

```sh
$ pip install canoser
```

## 使用

首先用Canoser定义一个数据结构，也就是写一个类继承自"canoser.Struct"，然后通过"_fields"来定义该结构所拥有的字段。该结构自然就拥有了序列化和反序列化的能力。例如下面的AccountResource定义了一个Libra代码中的同名数据结构：
```python
#python代码，利用canoser定义数据结构
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

下面是Libra中定义该数据结构以及序列化的代码：
```rust
// Libra中的rust语言代码
// 定义数据结构
pub struct AccountResource {
    balance: u64,
    sequence_number: u64,
    authentication_key: ByteArray,
    sent_events: EventHandle,
    received_events: EventHandle,
    delegated_withdrawal_capability: bool,
}
// 实现序列化
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
在Libra使用的rust语言中，需要手动写代码实现数据结构的序列化/反序列化，而且数据结构中的字段顺序和序列化时的顺序不一定一致。
在Canoser中，定义好数据结构后，不需要写序列化和反序列化的代码。注意，Canoser中的数据结构顺序要按照Libra中序列化的顺序来定义。

### 支持的数据类型

字段支持的类型有：

| 字段类型 | 可选子类型 | 说明 |
| ------ | ------ | ------ |
| canoser.Uint8 |  | 无符号8位整数 |
| canoser.Uint16 |  | 无符号16位整数 |
| canoser.Uint32 |  | 无符号32位整数 |
| canoser.Uint64 |  | 无符号64位整数 |
| canoser.Int8 |  | 有符号8位整数 |
| canoser.Int16 |  | 有符号16位整数 |
| canoser.Int32 |  | 有符号32位整数 |
| canoser.Int64 |  | 有符号64位整数 |
| bool |  | 布尔类型 |
| str |  | 字符串 |
| bytes |  | Binary String |
| [] | 支持 | 数组类型 |
| {} | 支持 |  Map类型 |
| A canoser.Struct |  | 嵌套的另外一个结构（不能循环引用） |

### 关于数组类型
数组里的数据，如果没有定义类型，那么缺省是Uint8。下面的两个定义等价：
```python
  class Arr1(Struct):
      _fields = [(addr, [])]


  class Arr2(Struct):
      _fields = [(addr, [Uint8])]

```  
数组还可以定义长度，表示定长数据。比如Libra中的地址是256位，也就是32个字节，所以可以如下定义：
```python
  class Address(Struct):
      _fields = [(addr, [Uint8, 32])]
```  
定长数据在序列化的时候，不写入长度信息。

### 关于Map类型
Map里的数据，如果没有定义类型，那么在libra中缺省是字节数组，也就是[Uint8]。
但是在python语言中，dict的key不支持list类型，于是在canoser中Map的key类型默认为bytes，value的类型是[Uint8]。下面的两个定义等价：
```python
  class Map1(Struct):
    _fields = [(addr, {})]


  class Map2(Struct):
    _fields = [(addr, {bytes : [Uint8] })]

```  

### 结构嵌套
下面是一个复杂的例子，包含三个数据结构：
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
这个例子参考自libra中canonical serialization的测试代码。

### 序列化和反序列化
在定义好canoser.Struct后，不需要自己实现序列化和反序列化代码，直接调用基类的默认实现即可。以AccountResource结构为例：
```python
#序列化
obj = AccountResource.new(authentication_key=...,...)
bbytes = obj.serialize
#反序列化
obj = AccountResource.deserialize(bbytes)
```
### 从Struct对象中读取字段的值
对于所有通过_field定义的字段，可以通过field_name获取该字段的值。比如：

```python
obj.authentication_key
```


