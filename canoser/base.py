from canoser.cursor import Cursor
from canoser.types import type_mapping
from io import StringIO

class Base:

    def serialize(self):
        return self.__class__.encode(self)

    @classmethod
    def deserialize(cls, buffer, check=True):
        cursor = Cursor(buffer)
        ret = cls.decode(cursor)
        if not cursor.is_finished() and check:
            raise IOError("bytes not all consumed:{}, {}".format(
                len(buffer), cursor.offset))
        return ret

    def __str__(self):
        concat = StringIO()
        self._pretty_print(concat, 0)
        return concat.getvalue()

    def _pretty_print_obj(self, value, concat, ident):
        prefix_blank = '  '
        if isinstance(value, dict):
            concat.write('{\n')
            ident_inner = ident+1
            for k,v in value.items():
                concat.write(prefix_blank*ident_inner)
                concat.write(f'{k}: ')
                self._pretty_print_obj(v, concat, ident_inner)
                concat.write(',\n')
            concat.write(prefix_blank*ident)
            concat.write('}')
            return
        if isinstance(value, list):
            concat.write('[\n')
            ident_inner = ident+1
            for item in enumerate(value):
                concat.write(prefix_blank*ident_inner)
                self._pretty_print_obj(item, concat, ident_inner)
                concat.write(',\n')
            concat.write(prefix_blank*ident)
            concat.write(']')
            return
        pprint = getattr(value, "_pretty_print", None)
        if callable(pprint):
            value._pretty_print(concat, ident)
        else:
            concat.write(f'{value}')

    def _pretty_print(self, concat, ident):
        pass