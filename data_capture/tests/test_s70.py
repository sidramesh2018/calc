import json
import copy

from copy import deepcopy
from decimal import Decimal
from unittest.mock import Mock, MagicMock, patch
from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError

from .common import path, XLSX_CONTENT_TYPE
from .test_models import ModelTestCase
from ..schedules import s70, registry


S70 = '%s.Schedule70PriceList' % s70.__name__

S70_XLSX_PATH = path('static', 'data_capture', 's70_example.xlsx')


def uploaded_xlsx_file(path=S70_XLSX_PATH, content=None):
    if content is None:
        with open(path, 'rb') as f:
            content = f.read()

    return SimpleUploadedFile(
        'foo.xlsx',
        content,
        content_type=XLSX_CONTENT_TYPE
    )


class FakeCell:
    def __init__(self, val):
        self._val = val

    @property
    def value(self):
        return self._val


class FakeSheet:
    def __init__(self, name=s70.DEFAULT_SHEET_NAME, cells=None):
        if cells is None:
            cells = deepcopy(s70.EXAMPLE_SHEET_ROWS)
        self.name = name
        self._cells = cells

    @property
    def nrows(self):
        return len(self._cells)

    def cell_value(self, rownum, colnum):
        return self._cells[rownum][colnum]

    def row(self, rownum):
        return [FakeCell(c) for c in self._cells[rownum]]


class FakeWorkbook:
    def __init__(self, sheets=None):
        if sheets is None:
            sheets = [FakeSheet()]
        self._sheets = sheets

    def sheet_names(self):
        return [sheet.name for sheet in self._sheets]

    def sheet_by_name(self, name):
        return [sheet for sheet in self._sheets if sheet.name == name][0]


class SafeCellStrValueTests(TestCase):
    def test_cell_value_index_errors_are_ignored(self):
        s = MagicMock()
        s.cell_value.side_effect = IndexError()

        self.assertEqual(s70.safe_cell_str_value(s, 99, 99), '')
        self.assertEqual(s.cell_value.call_count, 1)

    def test_coercer_value_errors_are_ignored(self):
        s = MagicMock()
        s.cell_value.return_value = 'blah'

        c = Mock()
        c.side_effect = ValueError()

        self.assertEqual(s70.safe_cell_str_value(s, 99, 99, c), 'blah')
        self.assertEqual(s.cell_value.call_count, 1)
        self.assertEqual(c.call_count, 1)

    def test_result_is_stringified(self):
        s = MagicMock()
        s.cell_value.return_value = 5

        self.assertEqual(s70.safe_cell_str_value(s, 1, 1), '5')

    def test_coercer_is_used(self):
        s = MagicMock()
        s.cell_value.return_value = 5.0

        self.assertEqual(s70.safe_cell_str_value(s, 1, 1, int), '5')


class TestGenerateColumnIndexMap(TestCase):
    def setUp(self):
        self.heading_row = [
            Mock(value='HEADING 2'),
            Mock(value='heading 1'),
            Mock(value='  Heading 3  '),
        ]

        self.field_title_map = {
            'field_1': 'heading 1',
            'field_2': 'heading 2',
            'field_3': 'heading 3',
        }

    def test_generate_column_index_map_works(self):
        col_idx_map = s70.generate_column_index_map(
            self.heading_row, field_title_map=self.field_title_map)
        self.assertEqual(col_idx_map, {
            'field_1': 1,
            'field_2': 0,
            'field_3': 2,
        })

    def test_raises_on_missing_field(self):
        map_with_additional_field = copy.copy(self.field_title_map)
        map_with_additional_field['missing_field'] = 'BOOP'
        with self.assertRaises(ValidationError):
            s70.generate_column_index_map(
                self.heading_row, field_title_map=map_with_additional_field)


class FindHeaderRowTests(TestCase):

    def return_heading_on_row_4(self, row, col):
        if row is 4:
            return s70.EXAMPLE_SHEET_ROWS[0][0]
        return 'boop'

    def test_find_header_row_works(self):
        sheet_mock = MagicMock(nrows=10)
        sheet_mock.cell_value.side_effect = self.return_heading_on_row_4
        self.assertEqual(s70.find_header_row(sheet_mock), 4)

    def test_raises_validation_error_if_table_not_found(self):
        sheet_mock = MagicMock(nrows=10)
        with self.assertRaises(ValidationError):
            s70.find_header_row(sheet_mock)

    def test_raises_validation_error_when_threshold_is_reached(self):
        sheet_mock = MagicMock(nrows=10)
        sheet_mock.cell_value.side_effect = self.return_heading_on_row_4
        with self.assertRaises(ValidationError):
            s70.find_header_row(sheet_mock, row_threshold=3)


class GleanLaborCategoriesTests(TestCase):
    def test_rows_are_returned(self):
        rows = s70.glean_labor_categories_from_file(uploaded_xlsx_file())
        self.assertEqual(rows, [{
            'sin': '132-51',
            'labor_category': 'Project Manager',
            'education_level': 'Bachelors',
            'min_years_experience': '5',
            'commercial_list_price': '125.0',
            'unit_of_issue': 'Hour',
            'most_favored_customer': 'All Commercial Customers',
            'best_discount': '0.07',
            'mfc_price': '123.99',
            'gsa_discount': '0.1',
            'price_excluding_iff': '110.99',
            'price_including_iff': '115.99',
            'volume_discount': '0.15',
        }])

    def test_text_formatted_prices_are_gleaned(self):
        book = FakeWorkbook()
        book._sheets[0]._cells[1][4] = '  $1,123.49  '
        book._sheets[0]._cells[1][8] = '$109.50'
        book._sheets[0]._cells[1][10] = ' $ 106.50'
        book._sheets[0]._cells[1][11] = '$107.50'

        rows = s70.glean_labor_categories_from_book(book)

        row = rows[0]

        self.assertEqual(row['commercial_list_price'], '1123.49')
        self.assertEqual(row['mfc_price'], '109.50')
        self.assertEqual(row['price_excluding_iff'], '106.50')
        self.assertEqual(row['price_including_iff'], '107.50')

    def test_min_education_is_gleaned_from_text(self):
        book = FakeWorkbook()
        book._sheets[0]._cells[1][2] = 'GED or high school diploma'

        rows = s70.glean_labor_categories_from_book(book)

        self.assertEqual(rows[0]['education_level'], 'High School')

    def test_validation_error_raised_when_sheet_not_present(self):
        with self.assertRaisesRegexp(
            ValidationError,
            r'There is no sheet in the workbook called "foo"'
        ):
            s70.glean_labor_categories_from_file(
                uploaded_xlsx_file(),
                sheet_name='foo'
            )


class LoadFromUploadValidationErrorTests(TestCase):
    @patch.object(s70, 'glean_labor_categories_from_file')
    def test_reraises_validation_errors(self, m):
        m.side_effect = ValidationError('foo')

        with self.assertRaisesRegexp(ValidationError, r'foo'):
            s70.Schedule70PriceList.load_from_upload(uploaded_xlsx_file())

    def test_raises_validation_error_on_corrupt_files(self):
        f = uploaded_xlsx_file(content=b'foo')

        with self.assertRaisesRegexp(
            ValidationError,
            r'An error occurred when reading your Excel data.'
        ):
            s70.Schedule70PriceList.load_from_upload(f)


@override_settings(DATA_CAPTURE_SCHEDULES=[S70])
class S70Tests(ModelTestCase):
    DEFAULT_SCHEDULE = S70

    def test_valid_rows_are_populated(self):
        p = s70.Schedule70PriceList.load_from_upload(uploaded_xlsx_file())

        self.assertEqual(len(p.valid_rows), 1)
        self.assertEqual(p.invalid_rows, [])

        self.assertEqual(p.valid_rows[0].cleaned_data, {
            'education_level': 'Bachelors',
            'labor_category': 'Project Manager',
            'min_years_experience': 5,
            'price_including_iff': Decimal('115.99'),
            'sin': '132-51'
        })

    def test_education_level_is_validated(self):
        p = s70.Schedule70PriceList(rows=[{'education_level': 'Batchelorz'}])

        self.assertRegexpMatches(
            p.invalid_rows[0].errors['education_level'][0],
            r'This field must contain one of the following values'
        )

    def test_min_years_experience_is_validated(self):
        p = s70.Schedule70PriceList(rows=[{'min_years_experience': ''}])

        self.assertEqual(p.invalid_rows[0].errors['min_years_experience'],
                         ['This field is required.'])

    def test_add_to_price_list_works(self):
        s = s70.Schedule70PriceList.load_from_upload(uploaded_xlsx_file())

        p = self.create_price_list()
        p.save()

        s.add_to_price_list(p)

        row = p.rows.all()[0]

        self.assertEqual(row.labor_category, 'Project Manager')
        self.assertEqual(row.education_level, 'BA')
        self.assertEqual(row.min_years_experience, 5)
        self.assertEqual(row.base_year_rate, Decimal('115.99'))
        self.assertEqual(row.sin, '132-51')

        row.full_clean()

    def test_serialize_and_deserialize_work(self):
        s = s70.Schedule70PriceList.load_from_upload(uploaded_xlsx_file())

        saved = json.dumps(registry.serialize(s))
        restored = registry.deserialize(json.loads(saved))

        self.assertTrue(isinstance(restored, s70.Schedule70PriceList))
        self.assertEqual(s.rows, restored.rows)

    def test_to_table_works(self):
        s = s70.Schedule70PriceList.load_from_upload(uploaded_xlsx_file())
        table_html = s.to_table()
        self.assertIsNotNone(table_html)
        self.assertTrue(isinstance(table_html, str))

    def test_to_error_table_works(self):
        s = s70.Schedule70PriceList.load_from_upload(uploaded_xlsx_file())
        table_html = s.to_error_table()
        self.assertIsNotNone(table_html)
        self.assertTrue(isinstance(table_html, str))

    def test_render_upload_example_works(self):
        html = s70.Schedule70PriceList.render_upload_example()
        self.assertTrue('Bachelors' in html)
