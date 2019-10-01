from canoser.cursor import Cursor
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
        self.__class__._pretty_print_obj(self, concat, 0)
        return concat.getvalue()
