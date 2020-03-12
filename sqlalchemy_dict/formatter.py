from datetime import datetime, timedelta, date, time

from sqlalchemy_dict.utils import to_camel_case
from sqlalchemy_dict.constants import (
    ISO_DATETIME_FORMAT,
    ISO_DATE_FORMAT,
    ISO_DATETIME_PATTERN,
    ISO_TIME_FORMAT,
)


class Formatter:
    """ Model formatter abstract class """

    @classmethod
    def export_key(cls, key):
        """
        Export dictionary key

        :param key: Model field name
        :return:
        """
        raise NotImplementedError  # pragma: no cover

    @classmethod
    def export_datetime(cls, value: datetime):
        """
        Export python datetime

        :param value:
        :return:
        """
        raise NotImplementedError  # pragma: no cover

    @classmethod
    def export_date(cls, value: date):
        """
        Export python date

        :param value:
        :return:
        """
        raise NotImplementedError  # pragma: no cover

    @classmethod
    def export_time(cls, value: time):
        """
        Export python time

        :param value:
        :return:
        """
        raise NotImplementedError  # pragma: no cover

    @classmethod
    def import_datetime(cls, value: [str, int]) -> datetime:
        """
        Import datetime field

        :param value:
        :return:
        """
        raise NotImplementedError  # pragma: no cover

    @classmethod
    def import_date(cls, value: [str, int]) -> date:
        """
        Import date

        :param value:
        :return:
        """
        raise NotImplementedError  # pragma: no cover

    @classmethod
    def import_time(cls, value: [str, int]) -> time:
        """
        Import time

        :param value:
        :return:
        """
        raise NotImplementedError  # pragma: no cover


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
        return value.isoformat()

    @classmethod
    def export_date(cls, value):
        return value.isoformat()

    @classmethod
    def export_time(cls, value):
        return value.isoformat()

    @classmethod
    def import_datetime(cls, value):
        match = ISO_DATETIME_PATTERN.match(value)
        if not match:
            raise ValueError("Invalid datetime format")

        res = datetime.strptime(match.group(1), ISO_DATETIME_FORMAT)
        if match.group(2) and len(match.group(2)) > 0:
            res = res.replace(microsecond=int(match.group(2)))

        return res

    @classmethod
    def import_date(cls, value):
        try:
            return datetime.strptime(value, ISO_DATE_FORMAT).date()
        except ValueError:
            raise ValueError("Invalid date format")

    @classmethod
    def import_time(cls, value):
        try:
            return datetime.strptime(value, ISO_TIME_FORMAT).time()
        except ValueError:
            raise ValueError("Invalid date format")
