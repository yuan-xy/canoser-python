import pdb

class TypedProperty:
    def __init__(self, name, expected_type):
        self.name = name
        self.expected_type = expected_type

    def __set__(self, instance, value):
        #pdb.set_trace()
        check = getattr(self.expected_type, "check_value", None)
        if callable(check):
            check(value)
        elif not isinstance(value, self.expected_type):
            raise TypeError('expected {0}, but {1}'.format(self.expected_type, type(value))) 
        instance.__dict__[self.name] = value


class Struct:
    _fields = []

    def __init__(self, *args, **kwargs):
        for name, atype in self._fields:
            setattr(self, name, TypedProperty(name, atype))

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

