from canoser.base import Base

class TupleT:

    def __init__(self, *ttypes):
        self.ttypes = ttypes

    def encode(self, value):
        output = b""
        zipped = zip(self.ttypes, value)
        for k, v in zipped:
            output += k.encode(v)
        return output

    def decode(self, cursor):
        arr = []
        for k in self.ttypes:
            arr.append(k.decode(cursor))
        return tuple(arr)

    def check_value(self, value):
        if len(value) != len(self.ttypes):
            raise TypeError(f"{len(value)} is not equal to {len(self.ttypes)}")
        if not isinstance(value, tuple):
            raise TypeError(f"{value} is not a tuple.")
        zipped = zip(self.ttypes, value)
        for k, v in zipped:
            k.check_value(v)

    def __eq__(self, other):
        if not isinstance(other, TupleT):
            return False
        zipped = zip(self.ttypes, other.ttypes)
        for t1, t2 in zipped:
            if t1 != t2:
                return False
        return True

    def pretty_print_obj(cls, obj, buffer, ident):
        prefix_blank = '  '
        buffer.write('(\n')
        ident_inner = ident+1
        zipped = zip(cls.ttypes, obj)
        for k, v in zipped:
            buffer.write(prefix_blank*ident_inner)
            if issubclass(k, Base):
                buffer.write(f'{k.__name__} ')
            k.pretty_print_obj(v, buffer, ident_inner)
            buffer.write(',\n')
        buffer.write(prefix_blank*ident)
        buffer.write(')')

    def to_json_serializable(cls, obj):
        ret = []
        #https://stackoverflow.com/questions/15721363/preserve-python-tuples-with-json
        #If need to deserialize tuple back later, above link will help.
        zipped = zip(cls.ttypes, obj)
        for k, v in zipped:
            data = Base.to_json_data(value_type=(v, k))
            ret.append(data)
        return ret
