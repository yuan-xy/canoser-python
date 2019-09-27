from canoser.cursor import Cursor
from canoser.types import type_mapping
from canoser.struct import TypedProperty
from canoser import *
from io import StringIO


import pdb

class RustEnum:
    _enums = []

    @classmethod
    def get_index(cls, name):
        for index, (ename, _) in enumerate(cls._enums):
            if ename == name:
                return index
        raise TypeError(f"name:{name} not in enum {cls}")

    @classmethod
    def new(cls, index, value):
        if not cls._enums:
            raise TypeError(f'{cls} has no _enums defined.')
        if index < 0 or index >= len(cls._enums):
            raise TypeError(f"index{index} out of bound:0-{len(cls._enums)-1}")
        _name, datatype = cls._enums[index]
        ret = cls.__new__(cls)
        ret._init_with_index_value(index, value, datatype)
        return ret

    def _init_with_index_value(self, index, value, datatype):
        self._index = index
        self.value_type = type_mapping(datatype)
        self.value = value

    def __init__(self, name, value=None):
        if not self.__class__._enums:
            raise TypeError(f'{self.__class__} has no _enums defined.')
        index = self.__class__.get_index(name)
        _name, datatype = self._enums[index]
        if name != _name:
            raise AssertionError(f"{name} != {_name}")
        self._init_with_index_value(index, value, datatype)

    def __getattr__(self, name):
        return self._index == self.__class__.get_index(name)

    def __setattr__(self, name, value):
        if name == "value":
            TypedProperty.check_type(self.value_type, value)
            self.__dict__[name] = value
        elif name == "_index" or name == "value_type":
            self.__dict__[name] = value
        else:
            raise TypeError(f"{name} not allowed to modify in {self}.")

    @property
    def index(self):
        return self._index

    @property
    def enum_name(self):
        name, _ = self.__class__._enums[self._index]
        return name

    @classmethod
    def encode(cls, enum):
        ret = Uint32.encode(enum.index)
        if enum.value_type is not None:
            ret += enum.value_type.encode(enum.value)
        return ret

    @classmethod
    def decode(cls, cursor):
        index = Uint32.decode(cursor)
        _name, datatype = cls._enums[index]
        if datatype is not None:
            value = type_mapping(datatype).decode(cursor)
            return cls.new(index, value)
        else:
            return cls.new(index, None)

    @classmethod
    def deserialize(self, buffer, check=True):
        cursor = Cursor(buffer)
        ret = self.decode(cursor)
        if not cursor.is_finished() and check:
            raise IOError("bytes not all consumed:{}, {}".format(len(buffer), cursor.offset))
        return ret

    @classmethod
    def check_value(cls, value):
        if not isinstance(value, cls):
            raise TypeError('value {} is not {} type'.format(value, cls))


    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.index == other.index and self.value == other.value

    def __str__(self):
        concat = StringIO()
        self._pretty_print(concat, 0)
        return concat.getvalue()

    def _pretty_print(self, concat, ident):
        concat.write(self.enum_name)
        pprint = getattr(self.value, "_pretty_print", None)
        if callable(pprint):
            self.value._pretty_print(concat, ident)
        else:
            concat.write(f'{self.value}')
