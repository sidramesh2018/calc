from unittest import TestCase
from django.test import TestCase as DjangoTestCase
from django.db import connection

from contracts.mommy_recipes import get_contract_recipe
from ..models import SubmittedPriceListRow
from ..analysis.finders import (
    ExactEduAndExpFinder,
    GteEduAndExpFinder,
)
from ..analysis.core import (
    find_comparable_contracts,
    describe,
    analyze_price_list_row,
)
from ..analysis.vocabulary import (
    Vocabulary,
    get_best_permutations,
)
from ..analysis.export import AnalysisExport, COMPARABLES_NOT_FOUND


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


class BaseDescribeTestCase(BaseDbTestCase):
    ROW_WITH_COMPARABLES = dict(
        labor_category='Engineer of Doom II',
        min_years_experience=5,
        education_level='BA',
        severe_stddevs=1,
        min_comparables=1,
        price=89
    )

    ROW_WITHOUT_COMPARABLES = dict(
        labor_category='zzzzzzzzzz',
        min_years_experience=0,
        education_level='AA',
        price=0
    )

    def describe(self, *args, **kwargs):
        return describe(
            self.cursor,
            self.vocab,
            *args,
            **kwargs
        )


class DescribeTests(BaseDescribeTestCase):
    def test_it_works_when_proposed_price_is_way_low(self):
        result = self.describe(**self.ROW_WITH_COMPARABLES)
        del result['description']
        self.assertEqual(result, {
            'avg': 90.0,
            'avg_exp': 5.0,
            'count': 1,
            'preposition': 'way below',
            'comparable_search_criteria': {'edu': 'BA', 'exp': '5-9 years'},
            'labor_category': 'Engineer of Doom II',
            'severe': True,
            'stddev': 1,
            'stddevs': 1,
            'url': '/?q=Engineer+of+Doom+II&min_experience=5'
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
            'avg_exp': 5.0,
            'count': 1,
            'comparable_search_criteria': {'edu': 'BA', 'exp': '5-9 years'},
            'labor_category': 'Engineer of Doom II',
            'severe': False,
            'stddev': 1,
            'stddevs': 0,
            'url': '/?q=Engineer+of+Doom+II&min_experience=5'
                   '&max_experience=9&education=BA',
        })

    def test_returns_empty_description_if_no_comparables_found(self):
        result = self.describe(**self.ROW_WITHOUT_COMPARABLES)
        self.assertEqual(result, {
            'severe': False,
            'description': ''
        })


class ExportTests(BaseDescribeTestCase):
    @staticmethod
    def to_spl_row(sin, **describe_kwargs):
        return SubmittedPriceListRow(
            sin=sin,
            labor_category=describe_kwargs['labor_category'],
            min_years_experience=describe_kwargs['min_years_experience'],
            education_level=describe_kwargs['education_level'],
            base_year_rate=describe_kwargs['price'],
        )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.setup_rows = False

    def setUp(self):
        if not self.setup_rows:
            self.setup_rows = True
            self.row_without_comparables = self.to_analyzed_row(
                self.to_spl_row('1234', **self.ROW_WITHOUT_COMPARABLES))
            self.row_with_comparables = self.to_analyzed_row(
                self.to_spl_row('5678', **self.ROW_WITH_COMPARABLES))
            self.rows = [
                self.row_without_comparables,
                self.row_with_comparables
            ]

    def to_analyzed_row(self, spl_row):
        return analyze_price_list_row(self.cursor, self.vocab, spl_row)

    def test_to_csv_works(self):
        response = AnalysisExport(self.rows).to_csv()
        self.assertEqual(response['Content-Disposition'],
                         'attachment; filename="analysis.csv"')
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertContains(response, 'Average Price')
        self.assertContains(response, '5678')

    def test_to_xlsx_works(self):
        response = AnalysisExport(self.rows).to_xlsx()
        self.assertEqual(response['Content-Disposition'],
                         'attachment; filename="analysis.xlsx"')
        self.assertEqual(response['Content-Type'],
                         'application/vnd.openxmlformats-'
                         'officedocument.spreadsheetml.sheet')

    def test_exporting_row_without_comparables_works(self):
        _, row = next(AnalysisExport([
            self.row_without_comparables]).to_output_rows())
        self.assertEqual(row.comparables, 0)
        self.assertEqual(row.search_labor_category, COMPARABLES_NOT_FOUND)
        self.assertEqual(row.exp_comparable_search_criteria, '')
        self.assertEqual(row.edu_comparable_search_criteria, '')
        self.assertEqual(row.avg_exp, '')

    def test_exporting_row_with_comparables_works(self):
        _, row = next(AnalysisExport([
            self.row_with_comparables]).to_output_rows())
        self.assertEqual(row.comparables, 2)
        self.assertEqual(row.search_labor_category, 'Engineer of Doom II')
        self.assertEqual(row.exp_comparable_search_criteria, '5-9 years')
        self.assertEqual(row.edu_comparable_search_criteria, 'BA')
        self.assertEqual(row.avg_exp, 5.0)


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
        self.assertEqual(fc.phrase, 'Engineer of Doom II')
        self.assertEqual(fc.count, 1)
        self.assertEqual(fc.finder.__class__, GteEduAndExpFinder)

    def test_broadening_education_works(self):
        fc = self.find_comparable_contracts(
            labor_category='Engineer of Doom II',
            min_years_experience=5,
            education_level='AA',
            min_count=1,
        )
        self.assertEqual(fc.phrase, 'Engineer of Doom II')
        self.assertEqual(fc.count, 1)
        self.assertEqual(fc.finder.__class__, GteEduAndExpFinder)

    def test_exact_match_searches_work(self):
        fc = self.find_comparable_contracts(
            labor_category='Engineer of Doom II',
            min_years_experience=5,
            education_level='BA',
            min_count=1,
        )
        self.assertEqual(fc.phrase, 'Engineer of Doom II')
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
