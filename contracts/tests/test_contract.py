from django.test import TestCase
from contracts.mommy_recipes import get_contract_recipe
from itertools import cycle

from ..models import Contract


class ContractTestCase(TestCase):

    def test_readable_business_size(self):
        business_sizes = ('O', 'S')
        contract1, contract2 = get_contract_recipe().make(
            _quantity=2, business_size=cycle(business_sizes))
        self.assertEqual(contract1.get_readable_business_size(),
                         'other than small business')
        self.assertEqual(
            contract2.get_readable_business_size(), 'small business')

    def test_get_education_code(self):
        c = get_contract_recipe().make()
        self.assertEqual(c.get_education_code('Bachelors'), 'BA')
        self.assertIsNone(c.get_education_code('Nursing'), None)

    def test_normalize_rate(self):
        c = get_contract_recipe().make()
        self.assertEqual(c.normalize_rate('$1,000.00,'), 1000.0)


class ContractSearchTestCase(TestCase):
    CATEGORIES = [
        'Sign Language Interpreter',
        'Foreign Language Staff Interpreter (Spanish sign language)',
        'Aircraft Servicer',
        'Service Order Dispatcher',
        'Disposal Services',
        'Interpretation Services Class 4: Afrikan,Akan,Albanian',
        'Interpretation Services Class 1: Spanish',
        'Interpretation Services Class 2: French, German, Italian',
    ]

    def assertCategoriesEqual(self, results, categories):
        self.assertEqual([
            result.labor_category
            for result in results
        ], categories)

    def setUp(self):
        self.contracts = get_contract_recipe().make(
            labor_category=cycle(self.CATEGORIES),
            _quantity=len(self.CATEGORIES)
        )

    def test_search_index_works_via_raw_sql(self):
        results = Contract.objects.raw(
            '''
            SELECT id, labor_category
            FROM contracts_contract
            WHERE search_index @@ to_tsquery('Interpretation')
            '''
        )
        self.assertCategoriesEqual(results, [
            u'Sign Language Interpreter',
            u'Foreign Language Staff Interpreter (Spanish sign language)',
            u'Interpretation Services Class 4: Afrikan,Akan,Albanian',
            u'Interpretation Services Class 1: Spanish',
            u'Interpretation Services Class 2: French, German, Italian'
        ])
