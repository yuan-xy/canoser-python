import pdb
from canoser.cursor import Cursor
from canoser.fields import *

class TypedProperty:
    def __init__(self, name, expected_type):
        self.name = name
        self.expected_type = expected_type

    def __set__(self, instance, value):
        check = getattr(self.expected_type, "check_value", None)
        if callable(check):
            check(value)
        elif not isinstance(value, self.expected_type):
            raise TypeError('expected {0}, but {1}'.format(self.expected_type, type(value))) 
        instance.__dict__[self.name] = value

def type_mapping(field_type):
    if field_type == str:
        return StrT
    elif field_type == bool:
        return BoolT
    elif type(field_type) == list:
        if len(field_type) == 0:
            item = Uint8
        elif len(field_type) == 1:
            item = field_type[0]
        else:
            raise TypeError("Array has one item type, no more.")
        return ArrayT(type_mapping(item))
    elif type(field_type) == dict:
        if len(field_type) == 0:
            ktype = Uint8
            vtype = Uint8
        elif len(field_type) == 1:
            ktype = next(iter(field_type.keys()))
            vtype = next(iter(field_type.values()))
        else:
            raise TypeError("Map type has one item mapping key type to value type.")
        return MapT(type_mapping(ktype), type_mapping(vtype))
    else:
        return field_type


class Struct:
    _fields = []
    _initialized = False

    def __init__(self, *args, **kwargs):
        if not self.__class__._initialized:
            self.__class__._initialized = True
            for name, atype in self._fields:
                setattr(self.__class__, name, TypedProperty(name, type_mapping(atype)))

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
            else:
                print("field `{}` not initialized.".format(name))
                pass

        # Check for any remaining unknown arguments
        if kwargs:
            raise TypeError('Invalid argument(s): {}'.format(','.join(kwargs)))

    def serialize(self):
        output = b''
        for name, atype in self._fields:
            value = getattr(self, name)
            output += type_mapping(atype).encode(value)
        return output

    @classmethod
    def deserialize(self, buffer):
        cursor = Cursor(buffer)
        ret = self.__new__(self)
        ret.__init__()
        ret.decode(cursor)
        if not cursor.is_finished():
            raise Error("bytes not all consumed.")
        return ret

    def decode(self, cursor):
        for name, atype in self._fields:
            prop = getattr(self, name)
            mtype = type_mapping(atype)
            assert mtype == prop.expected_type
            value = mtype.decode(cursor)
            prop.__set__(self, value)
