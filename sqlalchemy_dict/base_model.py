import functools

from typing import Union, Generator, Tuple, Any, Callable, List

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
    """
    BaseModel provides ``sqlalchemy_dict`` abilities ready for every ``sqlalchemy`` declarative models.

    This class should set to sqlalchemy `declarative_base
    <http://docs.sqlalchemy.org/en/latest/orm/extensions/declarative/api.html
    #sqlalchemy.ext.declarative.declarative_base.params.cls>`_
    as base class like this:

    .. code-block:: python

        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.sql.schema import MetaData

        metadata = MetaData()
        DeclarativeBase = declarative_base(cls=BaseModel, metadata=metadata)

    """

    #: Model formatter class. default is :class:`sqlalchemy_dict.formatter.DefaultFormatter`
    __formatter__ = DefaultFormatter

    @classmethod
    def get_dict_key(cls, column: Column) -> str:
        """
        Get column dictionary key.

        it uses column info if already ``dict_key`` was set.

        :param column:
        :return:
        """
        return cls.get_column_info(column).get('dict_key', cls.__formatter__.export_key(column.key))

    @classmethod
    def get_column(cls, column: Union[Column, str]):
        """
        Get column by its name, also accept Column type too.

        :param column:
        :return:
        """
        if isinstance(column, str):
            mapper = inspect(cls)
            return mapper.columns[column]
        return column

    @classmethod
    def get_column_info(cls, column: Column) -> dict:
        """
        Get column info, it will merge `info` from proxy properties
        :param column:
        :return:
        """
        # Use original property for proxies
        if hasattr(column, 'original_property') and column.original_property:
            info = column.info.copy()
            info.update(column.original_property.info)
        else:
            info = column.info

        return info

    @classmethod
    def import_value(cls, column: Union[Column, str], v):
        """
        Import value for a column.
        :param column:
        :param v:
        :return:
        """
        c = cls.get_column(column)
        if isinstance(c, Column) or isinstance(c, InstrumentedAttribute):
            try:
                if c.type.python_type is bool and not isinstance(v, bool) and v is not None:
                    return str(v).lower() == 'true'
            except NotImplementedError:
                pass
        return v

    @classmethod
    def prepare_for_export(cls, column: Column, v) -> tuple:
        """
        Prepare column value to export.

        :param column:
        :param v:
        :return: Returns tuple of column dictionary key and value
        """
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

        return cls.get_dict_key(column), result

    def update_from_dict(self, context: dict):
        """
        Update model instance from dictionary.

        :param context:
        :return:
        """
        for column, value in self.extract_data_from_dict(context):
            setattr(
                self,
                column.key[1:] if column.key.startswith('_') else column.key,
                self.import_value(column, value)
            )

    @classmethod
    def iter_columns(cls, relationships=True, synonyms=True, composites=True,
                     use_inspection=True, hybrids=True) -> Generator[Column, None, None]:
        """
        Iterate model columns.

        :param relationships: Include relationships
        :param synonyms: Include synonyms
        :param composites: Include composites
        :param use_inspection: Force to use ``sqlalchemy`` inspector
        :param hybrids: Include hybrids
        :return: 
        """
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
    def iter_dict_columns(cls, include_readonly_columns=True,
                          include_protected_columns=False, **kw) -> Generator[Column, None, None]:
        """
        Same as :func:`BaseModel.iter_columns` but have options to include
        ``readonly`` and ``protected`` columns.

        :param include_readonly_columns:
        :param include_protected_columns:
        :param kw:
        :return:
        """
        for column in cls.iter_columns(**kw):
            info = cls.get_column_info(column)

            if (not include_protected_columns and info.get('protected')) or \
                    (not include_readonly_columns and info.get('readonly')):
                continue

            yield column

    @classmethod
    def extract_data_from_dict(cls, context: dict) -> Generator[Tuple[Column, Any], None, None]:
        """
        Extract values from dictionary.

        :param context:
        :return: Tuple of diction
        """
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

    def to_dict(self) -> dict:
        """
        Convert model instance to dictionary.

        :return:
        """
        result = {}
        for c in self.iter_dict_columns():
            result.setdefault(*self.prepare_for_export(c, getattr(self, c.key)))
        return result

    @classmethod
    def dump_query(cls, query: Query) -> List[dict]:
        """
        Dump query results in a list of model dictionaries.

        :param query:
        :return:
        """
        return [o.to_dict() for o in query]

    @classmethod
    def expose(cls, func: Callable) -> Callable:
        """
        A decorator to automatically convert model instance or query to dictionary or list of dictionaries.

        :param func:
        :return:
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            if hasattr(result, 'to_dict'):
                return result.to_dict()

            if isinstance(result, Query):
                return cls.dump_query(result)
            return result

        return wrapper
