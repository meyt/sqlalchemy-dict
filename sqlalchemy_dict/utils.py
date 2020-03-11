
import re
from datetime import datetime, timedelta

ZERO = timedelta(0)


def format_iso_datetime(stamp):
    """ Return a string representing the date and time in ISO 8601 format.
        If the time is in UTC, adds a 'Z' directly after the time without
        a space.
        see http://en.wikipedia.org/wiki/ISO_8601.
        >>> from datetime import tzinfo
        ... # noinspection PyAbstractClass
        ... class EET(tzinfo):
        ...     def utcoffset(self, dt):
        ...         return timedelta(minutes=120)
        ...     def dst(self, dt):
        ...         return timedelta()
        ... # noinspection PyAbstractClass
        ... class UTC(tzinfo):
        ...     def utcoffset(self, dt):
        ...         return ZERO
        ...     def dst(self, dt):
        ...         return ZERO
        >>> format_iso_datetime(datetime(2012, 2, 22, 12, 52, 29, 300))
        '2012-02-22T12:52:29'
        >>> format_iso_datetime(datetime(2012, 2, 22, 12, 52, 29, 300,
        ...     tzinfo=UTC))
        '2012-02-22T12:52:29Z'
        >>> format_iso_datetime(datetime(2012, 2, 22, 12, 52, 29, 300,
        ...     tzinfo=EET()))
        '2012-02-22T12:52:29+02:00'
    """
    if stamp.tzinfo:
        if stamp.utcoffset() == ZERO:
            return datetime(*stamp.timetuple()[:7]).isoformat() + 'Z'

    return stamp.isoformat()


def format_iso_time(stamp):
    """ Return a string representing the time in ISO 8601 format.
        If the time is in UTC, adds a 'Z' directly after the time without
        a space.
        see http://en.wikipedia.org/wiki/ISO_8601.
        >>> from datetime import time, tzinfo
        ... # noinspection PyAbstractClass
        ... class EET(tzinfo):
        ...     def utcoffset(self, dt):
        ...         return timedelta(minutes=120)
        ...     def dst(self, dt):
        ...         return timedelta()
        ... # noinspection PyAbstractClass
        ... class UTC(tzinfo):
        ...     def utcoffset(self, dt):
        ...         return ZERO
        ...     def dst(self, dt):
        ...         return ZERO
        >>> format_iso_time(time(12, 52, 29, 300))
        '12:52:29'
        >>> format_iso_time(time(12, 52, 29, 300,
        ...     tzinfo=UTC))
        '12:52:29Z'
        >>> format_iso_time(time(12, 52, 29, 300,
        ...     tzinfo=EET()))
        '12:52:29+02:00'
    """
    if stamp.tzinfo:
        if stamp.utcoffset() == ZERO:
            return stamp.replace(tzinfo=None).isoformat() + 'Z'
        else:
            return stamp.isoformat()
    else:
        return stamp.isoformat()


def to_camel_case(text):
    return re.sub("(_\w)", lambda x: x.group(1)[1:].upper(), text)
