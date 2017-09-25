import unittest
from datetime import datetime, timezone, timedelta, time
from sqlalchemy_dict.utils import format_iso_datetime, format_iso_time


class UtilsTestCase(unittest.TestCase):

    def test_format_iso_datetime(self):
        result = format_iso_datetime(datetime(2012, 2, 22, 12, 52, 29, 300, tzinfo=timezone(timedelta(minutes=30))))
        self.assertEqual(result, '2012-02-22T12:52:29+00:30')

        result = format_iso_datetime(datetime(2012, 2, 22, 12, 52, 29, 300, tzinfo=timezone(timedelta(minutes=0))))
        self.assertEqual(result, '2012-02-22T12:52:29Z')

    def test_format_iso_time(self):
        result = format_iso_time(time(12, 52, 29, 300, tzinfo=timezone(timedelta(minutes=30))))
        self.assertEqual(result, '12:52:29+00:30')

        result = format_iso_time(time(12, 52, 29, 300, tzinfo=timezone(timedelta(minutes=0))))
        self.assertEqual(result, '12:52:29Z')


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
