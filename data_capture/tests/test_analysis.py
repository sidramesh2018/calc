from unittest import TestCase
from django.test import TestCase as DjangoTestCase
from django.db import connection

from contracts.mommy_recipes import get_contract_recipe
from ..analysis.core import (
    find_comparable_contracts,
)
from ..analysis.vocabulary import (
    Vocabulary,
    get_best_permutations,
)


class FindComparableContractsTests(DjangoTestCase):
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
            min_years_experience=4,
            education_level="BA",
            current_price=100
        )
        cls.cursor = connection.cursor()
        cls.vocab = Vocabulary.from_db(cls.cursor, min_ndoc=1)

    def find_comparable_contracts(self, *args, **kwargs):
        return find_comparable_contracts(
            self.cursor,
            self.vocab,
            *args,
            **kwargs
        )

    def test_exact_match_searches_work(self):
        phrase, contracts, count = self.find_comparable_contracts(
            labor_category='Engineer of Doom II',
            min_years_experience=5,
            education_level='BA',
            min_count=1,
        )
        self.assertEqual(phrase, 'Engineer Doom II')
        self.assertEqual(count, 1)

    def test_broadening_labor_category_works(self):
        phrase, contracts, count = self.find_comparable_contracts(
            labor_category='Engineer of Doom II',
            min_years_experience=5,
            education_level='BA',
            min_count=2,
        )
        self.assertEqual(phrase, 'Engineer II')
        self.assertEqual(count, 2)

    def test_returns_nothing_if_no_matches_found(self):
        phrase, contracts, count = self.find_comparable_contracts(
            labor_category='zzzzzzzzzz',
            min_years_experience=0,
            education_level='AA',
        )
        self.assertEqual((phrase, contracts, count), (None, None, None))


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
