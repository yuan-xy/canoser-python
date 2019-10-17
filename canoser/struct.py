from canoser.base import Base
from canoser.cursor import Cursor
from canoser.types import type_mapping
from io import StringIO


class TypedProperty:
    def __init__(self, name, expected_type):
        self.name = name
        self.expected_type = expected_type

    def __set__(self, instance, value):
        TypedProperty.check_type(self.expected_type, value)
        instance.__dict__[self.name] = value

    @staticmethod
    def check_type(datatype, value):
        if datatype is None:
            if value is not None:
                raise TypeError(f'{datatype} mismatch {value}')
            else:
                return
        check = getattr(datatype, "check_value", None)
        if callable(check):
            check(value)
        else:
            raise TypeError('{} has no check_value method'.format(datatype))



class Struct(Base):
    _fields = []
    _initialized = False

    @classmethod
    def initailize_fields_type(cls):
        if not cls._initialized:
            cls._initialized = True
            for name, atype in cls._fields:
                setattr(cls, name, TypedProperty(name, type_mapping(atype)))

    def __init__(self, *args, **kwargs):
        self.__class__.initailize_fields_type()

        if len(args) > len(self._fields):
            raise TypeError('Expected {} arguments'.format(len(self._fields)))

        # Set all of the positional arguments
        for (name, _type), value in zip(self._fields, args):
            typed = getattr(self, name)
            typed.__set__(self, value)

        # Set the remaining keyword arguments
        for name, _type in self._fields[len(args):]:
            if name in kwargs:
                typed = getattr(self, name)
                typed.__set__(self, kwargs.pop(name))

        # Check for any remaining unknown arguments
        if kwargs:
            raise TypeError('Invalid argument(s): {}'.format(','.join(kwargs)))


    @classmethod
    def encode(cls, obj):
        output = b''
        for name, atype in obj._fields:
            value = getattr(obj, name)
            output += type_mapping(atype).encode(value)
        return output

    @classmethod
    def decode(cls, cursor):
        ret = cls.__new__(cls)
        ret.__init__()
        for name, atype in ret._fields:
            prop = getattr(ret, name)
            mtype = type_mapping(atype)
            assert mtype == prop.expected_type
            value = mtype.decode(cursor)
            prop.__set__(ret, value)
        return ret

    @classmethod
    def check_value(cls, value):
        if not isinstance(value, cls):
            raise TypeError('value {} is not {} type'.format(value, cls))

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        for name, atype in self._fields:
            v1 = getattr(self, name)
            v2 = getattr(other, name)
            if v1 != v2:
                return False
        return True

    @classmethod
    def pretty_print_obj(cls, obj, buffer, ident):
        #TODO obj should be instance of cls
        prefix_blank = '  '
        #buffer.write(prefix_blank*ident)
        buffer.write('{\n')
        ident_inner = ident+1
        for name, atype in obj._fields:
            value = getattr(obj, name)
            buffer.write(prefix_blank*ident_inner)
            cls.pretty_print_field(name, type_mapping(atype), value, buffer, ident_inner)
            buffer.write(',\n')
        buffer.write(prefix_blank*ident)
        buffer.write('}')

    @classmethod
    def pretty_print_field(cls, field_name, field_type, field_value, buffer, ident):
        buffer.write(f'{field_name}: ')
        field_type.pretty_print_obj(field_value, buffer, ident)

    def to_json_serializable(self):
        amap = {}
        for name, atype in self._fields:
            value = getattr(self, name)
            atype = type_mapping(atype)
            amap[name] = Base.to_json_data(value_type=(value, atype))
        return amap


