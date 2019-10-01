from canoser.types import type_mapping


class DelegateT:
    delegate_type = 'delegate'

    @classmethod
    def dtype(cls):
        return type_mapping(cls.delegate_type)

    @classmethod
    def encode(cls, value):
        return cls.dtype().encode(value)

    @classmethod
    def decode(cls, cursor):
        return cls.dtype().decode(cursor)

    @classmethod
    def check_value(cls, value):
        cls.dtype().check_value(value)

    @classmethod
    def _pretty_print_obj(cls, obj, concat, ident):
        cls.dtype()._pretty_print_obj(obj, concat, ident)

