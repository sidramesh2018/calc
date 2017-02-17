from datetime import datetime

from django.test import TestCase

from ..templatetags.data_capture import tz_timestamp


class ReadableTimestampTests(TestCase):
    def test_it_works(self):
        utc_datetime = datetime(2016, 2, 11, 14, 30, 5)
        val = tz_timestamp(utc_datetime)
        self.assertEqual(val, 'Feb. 11, 2016, 9:30 a.m. (EST)')

    def test_it_returns_orig_value_when_not_datetime(self):
        val = tz_timestamp('abc')
        self.assertEqual(val, 'abc')

    def test_timezone_name_can_be_specified(self):
        utc_datetime = datetime(2016, 2, 11, 14, 30, 5)
        val = tz_timestamp(utc_datetime, "US/Central")
        self.assertEqual(val, 'Feb. 11, 2016, 8:30 a.m. (CST)')
