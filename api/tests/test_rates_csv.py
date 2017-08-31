
from django.test import TestCase

from .test_rates_api import GetRatesTests

RATES_CSV_PATH = '/api/rates/csv'


# TODO: These tests need to be more fully fleshed out
class GetRatesCSVTests(TestCase):
    def setUp(self):
        GetRatesTests.make_test_set()
        self.path = RATES_CSV_PATH

    def test_prefixes_excel_formula_chars(self):
        excel_formula_prefixes = ['@', '-', '=', '|', '%']
        for char in excel_formula_prefixes:
            resp = self.client.get(f'{self.path}/?q={char}query')
            self.assertContains(resp, f"'{char}query")
