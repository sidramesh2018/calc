import urllib

from django.test import TestCase

from .test_rates_api import GetRatesTests

RATES_CSV_PATH = '/api/rates/csv'


# TODO: These tests need to be more fully fleshed out
class GetRatesCSVTests(TestCase):
    def setUp(self):
        GetRatesTests.make_test_set()
        self.path = RATES_CSV_PATH

    def test_prefixes_excel_formula_chars_in_query(self):
        excel_formula_prefixes = ['@', '+', '-', '=', '|', '%']
        for char in excel_formula_prefixes:
            encoded_query = urllib.parse.quote(f'{char}query')
            resp = self.client.get(f'{self.path}/?q={encoded_query}')
            self.assertContains(resp, f"'{char}query")
