import functools
from datetime import datetime, date, time
from decimal import Decimal

from sqlalchemy import Column
from sqlalchemy.orm import Query, CompositeProperty
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.relationships import RelationshipProperty
from sqlalchemy.ext.hybrid import HYBRID_PROPERTY
from sqlalchemy.ext.associationproxy import ASSOCIATION_PROXY
from sqlalchemy.inspection import inspect
from sqlalchemy_dict import DefaultFormatter


class BaseModel(object):
    __formatter__ = DefaultFormatter

    @classmethod
    def get_dict_key(cls, column):
        return column.info.get('dict_key', cls.__formatter__.export_key(column.key))

    @classmethod
    def get_column(cls, column):
        if isinstance(column, str):
            mapper = inspect(cls)
            return mapper.columns[column]
        return column

    @classmethod
    def import_value(cls, column, v):
        c = cls.get_column(column)
        if isinstance(c, Column) or isinstance(c, InstrumentedAttribute):
            try:
                if c.type.python_type is bool and not isinstance(v, bool):
                    return str(v).lower() == 'true'
            except NotImplementedError:
                pass
        return v

    @classmethod
    def prepare_for_export(cls, column, v):
        param_name = cls.get_dict_key(column)
        if hasattr(column, 'property') and isinstance(column.property,
                                                      RelationshipProperty) and column.property.uselist:
            result = [c.to_dict() for c in v]

        elif hasattr(column, 'property') and isinstance(column.property, CompositeProperty):
            result = v.__composite_values__()

        elif v is None:
            result = v

        elif isinstance(v, datetime):
            result = cls.__formatter__.export_datetime(v)

        elif isinstance(v, date):
            result = cls.__formatter__.export_date(v)

        elif isinstance(v, time):
            result = cls.__formatter__.export_time(v)

        elif hasattr(v, 'to_dict'):
            result = v.to_dict()

        elif isinstance(v, Decimal):
            result = str(v)

        else:
            result = v

        return param_name, result

    def update_from_dict(self, context):
        for column, value in self.extract_data_from_dict(context):
            setattr(
                self,
                column.key[1:] if column.key.startswith('_') else column.key,
                self.import_value(column, value)
            )

    @classmethod
    def iter_columns(cls, relationships=True, synonyms=True, composites=True, use_inspection=True, hybrids=True):
        if use_inspection:
            mapper = inspect(cls)
            for k, c in mapper.all_orm_descriptors.items():

                if k == '__mapper__':
                    continue

                if c.extension_type == ASSOCIATION_PROXY:
                    continue

                if (not hybrids and c.extension_type == HYBRID_PROPERTY) \
                        or (not relationships and k in mapper.relationships) \
                        or (not synonyms and k in mapper.synonyms) \
                        or (not composites and k in mapper.composites):
                    continue
                yield getattr(cls, k)

        else:
            # noinspection PyUnresolvedReferences
            for c in cls.__table__.c:
                yield c

    @classmethod
    def iter_dict_columns(cls, include_readonly_columns=True, include_protected_columns=False, **kw):
        for c in cls.iter_columns(**kw):
            info = c.info
            # Use original property for proxies
            if hasattr(c, 'original_property') and c.original_property:
                info = c.original_property.info

            if (not include_protected_columns and info.get('protected')) or \
                    (not include_readonly_columns and info.get('readonly')):
                continue

            yield c

    @classmethod
    def extract_data_from_dict(cls, context):
        for c in cls.iter_dict_columns(include_protected_columns=True, include_readonly_columns=False):
            param_name = cls.get_dict_key(c)

            if param_name in context:
                value = context[param_name]
                # Ensuring the python type, and ignoring silently if python type is not specified
                try:
                    c.type.python_type
                except NotImplementedError:
                    yield c, value
                    continue

                if c.type.python_type == datetime:
                    yield c, cls.__formatter__.import_datetime(value)

                elif c.type.python_type == date:
                    yield c, cls.__formatter__.import_date(value)

                elif c.type.python_type == time:
                    yield c, cls.__formatter__.import_time(value)

                else:
                    yield c, value

    def to_dict(self):
        result = {}
        for c in self.iter_dict_columns():
            result.setdefault(*self.prepare_for_export(c, getattr(self, c.key)))
        return result

    @classmethod
    def dump_query(cls, query=None):
        result = []
        for o in query:
            result.append(o.to_dict())
        return result

    @classmethod
    def expose(cls, func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            if hasattr(result, 'to_dict'):
                return result.to_dict()

            if isinstance(result, Query):
                return cls.dump_query(result)
            return result

        return wrapper
