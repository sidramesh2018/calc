from unittest.mock import patch
from unittest import TestCase

from ..schedules import base
from ..schedules.base import BasePriceList


class BasePriceListTests(TestCase):
    def test_is_empty_returns_true_when_empty(self):
        pl = BasePriceList()
        self.assertTrue(pl.is_empty())

    def test_is_empty_returns_false_when_valid_rows_exist(self):
        pl = BasePriceList()
        pl.valid_rows = ['blah']
        self.assertFalse(pl.is_empty())

    def test_is_empty_returns_false_when_invalid_rows_exist(self):
        pl = BasePriceList()
        pl.invalid_rows = ['blah']
        self.assertFalse(pl.is_empty())

    def test_render_upload_example_returns_empty_string_by_default(self):
        self.assertEqual(BasePriceList.render_upload_example(), '')

    @patch.object(base, 'render_to_string')
    def test_render_upload_example_calls_render_to_string(self, r):
        class FunkyPriceList(BasePriceList):
            upload_example_template = 'foo/bar.html'

        r.return_value = 'blah'

        self.assertEqual(FunkyPriceList.render_upload_example(), 'blah')

        r.assert_called_once_with('foo/bar.html')
