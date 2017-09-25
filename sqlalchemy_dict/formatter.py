from datetime import datetime, timedelta

from sqlalchemy_dict.utils import format_iso_datetime, format_iso_time, to_camel_case
from sqlalchemy_dict.constants import ISO_DATETIME_FORMAT, ISO_DATE_FORMAT, ISO_DATETIME_PATTERN


class Formatter:

    @classmethod
    def export_key(cls, key):
        raise NotImplemented

    @classmethod
    def export_datetime(cls, value):
        raise NotImplemented

    @classmethod
    def export_date(cls, value):
        raise NotImplemented

    @classmethod
    def export_time(cls, value):
        raise NotImplemented

    @classmethod
    def import_datetime(cls, value):
        raise NotImplemented

    @classmethod
    def import_date(cls, value):
        raise NotImplemented

    @classmethod
    def import_time(cls, value):
        raise NotImplemented


class DefaultFormatter(Formatter):
    """
    Default Formatter
    """
    _zero = timedelta()

    @classmethod
    def export_key(cls, key):
        return to_camel_case(key)

    @classmethod
    def export_datetime(cls, value):
        return format_iso_datetime(value)

    @classmethod
    def export_date(cls, value):
        return value.isoformat()

    @classmethod
    def export_time(cls, value):
        return format_iso_time(value)

    @classmethod
    def import_datetime(cls, value):
        match = ISO_DATETIME_PATTERN.match(value)
        if not match:
            raise ValueError('Invalid datetime format')
        return datetime.strptime(match.groups()[0], ISO_DATETIME_FORMAT)

    @classmethod
    def import_date(cls, value):
        try:
            return datetime.strptime(value, ISO_DATE_FORMAT).date()
        except ValueError:
            raise ValueError('Invalid date format')

    @classmethod
    def import_time(cls, value):
        pass
