from unittest import TestCase
from django.test import TestCase as DjangoTestCase
from django.db import connection

from contracts.mommy_recipes import get_contract_recipe
from ..analysis.finders import (
    ExactEduAndExpFinder,
    GteEduAndExpFinder,
)
from ..analysis.core import (
    find_comparable_contracts,
    describe,
)
from ..analysis.vocabulary import (
    Vocabulary,
    get_best_permutations,
)


class BaseDbTestCase(DjangoTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.contract = get_contract_recipe()
        cls.contract.make(
            labor_category="Engineer of Doom II",
            min_years_experience=5,
            education_level="BA",
            current_price=90
        )
        cls.contract.make(
            labor_category="Engineer II",
            min_years_experience=5,
            education_level="BA",
            current_price=100
        )
        cls.cursor = connection.cursor()
        cls.vocab = Vocabulary.from_db(cls.cursor, min_ndoc=1)


class DescribeTests(BaseDbTestCase):
    def describe(self, *args, **kwargs):
        return describe(
            self.cursor,
            self.vocab,
            *args,
            **kwargs
        )

    def test_it_works_when_proposed_price_is_way_low(self):
        result = self.describe(
            labor_category='Engineer of Doom II',
            min_years_experience=5,
            education_level='BA',
            severe_stddevs=1,
            min_comparables=1,
            price=89
        )
        del result['description']
        self.assertEqual(result, {
            'avg': 90.0,
            'count': 1,
            'preposition': 'way below',
            'labor_category': 'Engineer Doom II',
            'severe': True,
            'stddev': 1,
            'stddevs': 1,
            'url': '/?q=Engineer+Doom+II&min_experience=5'
                   '&max_experience=9&education=BA'
        })

    def test_it_does_not_explode_when_stddev_is_zero(self):
        result = self.describe(
            labor_category='Engineer of Doom II',
            min_years_experience=5,
            education_level='BA',
            severe_stddevs=1,
            min_comparables=1,
            price=90
        )
        del result['description']
        self.assertEqual(result, {
            'avg': 90.0,
            'count': 1,
            'labor_category': 'Engineer Doom II',
            'severe': False,
            'stddev': 1,
            'stddevs': 0,
            'url': '/?q=Engineer+Doom+II&min_experience=5'
                   '&max_experience=9&education=BA'
        })

    def test_returns_empty_description_if_no_comparables_found(self):
        result = self.describe(
            labor_category='zzzzzzzzzz',
            min_years_experience=0,
            education_level='AA',
            price=0
        )
        self.assertEqual(result, {
            'severe': False,
            'description': ''
        })


class FindComparableContractsTests(BaseDbTestCase):
    def find_comparable_contracts(self, *args, **kwargs):
        return find_comparable_contracts(
            self.cursor,
            self.vocab,
            *args,
            **kwargs
        )

    def test_broadening_experience_works(self):
        fc = self.find_comparable_contracts(
            labor_category='Engineer of Doom II',
            min_years_experience=0,
            education_level='BA',
            min_count=1,
        )
        self.assertEqual(fc.phrase, 'Engineer Doom II')
        self.assertEqual(fc.count, 1)
        self.assertEqual(fc.finder.__class__, GteEduAndExpFinder)

    def test_broadening_education_works(self):
        fc = self.find_comparable_contracts(
            labor_category='Engineer of Doom II',
            min_years_experience=5,
            education_level='AA',
            min_count=1,
        )
        self.assertEqual(fc.phrase, 'Engineer Doom II')
        self.assertEqual(fc.count, 1)
        self.assertEqual(fc.finder.__class__, GteEduAndExpFinder)

    def test_exact_match_searches_work(self):
        fc = self.find_comparable_contracts(
            labor_category='Engineer of Doom II',
            min_years_experience=5,
            education_level='BA',
            min_count=1,
        )
        self.assertEqual(fc.phrase, 'Engineer Doom II')
        self.assertEqual(fc.count, 1)
        self.assertEqual(fc.finder.__class__, ExactEduAndExpFinder)

    def test_broadening_labor_category_works(self):
        fc = self.find_comparable_contracts(
            labor_category='Engineer of Doom II',
            min_years_experience=5,
            education_level='BA',
            min_count=2,
        )
        self.assertEqual(fc.phrase, 'Engineer II')
        self.assertEqual(fc.count, 2)
        self.assertEqual(fc.finder.__class__, ExactEduAndExpFinder)

    def test_returns_nothing_if_no_matches_found(self):
        fc = self.find_comparable_contracts(
            labor_category='zzzzzzzzzz',
            min_years_experience=0,
            education_level='AA',
        )
        self.assertEqual(fc, None)


class GteEduAndExpFinderTests(TestCase):
    def test_get_valid_education_levels_works(self):
        finder = GteEduAndExpFinder(1, 'AA')
        self.assertEqual(finder.get_valid_education_levels(),
                         ['AA', 'BA', 'MA', 'PHD'])

    def test_get_data_explorer_qs_params_works(self):
        finder = GteEduAndExpFinder(1, 'MA')
        self.assertEqual(finder.get_data_explorer_qs_params(), (
            ('min_experience', '1'),
            ('education', 'MA,PHD')
        ))


class GetBestPermutationsTests(TestCase):
    def test_min_length_works(self):
        vocab = Vocabulary.from_list([
            'engineer',
            'engineer ii',
        ])

        self.assertEqual(
            get_best_permutations(vocab, ['engineer', 'ii'], min_length=3),
            [('engineer', 'ii'),
             ('engineer',)],
        )

    def test_max_permutations_works(self):
        vocab = Vocabulary.from_list([
            'junior engineer',
            'junior awesome engineer',
            'engineer'
        ])

        self.assertEqual(
            get_best_permutations(vocab, ['junior', 'awesome',
                                          'engineer'], max_permutations=2),
            [('junior', 'awesome', 'engineer'),
             ('junior', 'engineer')]
        )

    def test_it_works(self):
        vocab = Vocabulary.from_list([
            'junior engineer',
            'engineer ii',
            'administrative assistant ii',
            'administrative assistant ii',
            'senior engineer',
            'project manager ii',
        ])
        self.assertEqual(
            get_best_permutations(vocab, ['junior', 'administrative',
                                          'engineer']),
            [('junior', 'engineer'),
             ('engineer',),
             ('administrative',),
             ('junior',)]
        )
