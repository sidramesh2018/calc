from django.test import TestCase
from django.core.exceptions import ValidationError

from .common import path, uploaded_xlsx_file, FakeWorkbook, FakeSheet
from ..schedules import region_10 as r10

R10_XLSX_PATH = path('static', 'data_capture', 'r10_example.xlsx')

# TODO: These tests should be DRY'd out since they nearly identical to test_s70
# Or really the shared methods should be generalized and those should be
# tested.


class GleaningTests(TestCase):
    def create_fake_book(self):
        return FakeWorkbook(sheets=[
            FakeSheet(r10.DEFAULT_SHEET_NAME, r10.EXAMPLE_SHEET_ROWS)])

    def test_rows_are_returned(self):
        rows = r10.glean_labor_categories_from_file(
            uploaded_xlsx_file(R10_XLSX_PATH))

        self.assertEqual(rows, [{
            'education_level': 'Professional Certification',
            'sin': '123-1',
            'min_years_experience': '2',
            'labor_category': 'Consultant II',
            'unit_of_issue': 'Hour',
            'price_including_iff': '90.6801007556675'  # TODO: blarf
            },
            {
            'education_level': 'None',
            'sin': '123-2',
            'min_years_experience': '0',
            'labor_category': 'Disposal Services',
            'unit_of_issue': 'Task',
            'price_including_iff': '0.0'
        }])

    def test_text_formatted_prices_are_gleaned(self):
        book = self.create_fake_book()
        book._sheets[0]._cells[1][13] = '$  37.50 '
        rows = r10.glean_labor_categories_from_book(book)
        self.assertEqual(rows[0]['price_including_iff'], '37.50')

    def test_min_education_is_gleaned_from_text(self):
        book = self.create_fake_book()
        book._sheets[0]._cells[1][2] = 'GED or high school or whatever'
        rows = r10.glean_labor_categories_from_book(book)
        self.assertEqual(rows[0]['education_level'], 'High School')

    def test_unit_of_issue_is_gleaned_to_hour(self):
        book = self.create_fake_book()
        book._sheets[0]._cells[1][7] = 'Hourly'

        rows = r10.glean_labor_categories_from_book(book)
        self.assertEqual(rows[0]['unit_of_issue'], 'Hour')

    def test_validation_error_raised_when_sheet_not_present(self):
        with self.assertRaisesRegexp(
            ValidationError,
            r'There is no sheet in the workbook called "foo"'
        ):
            r10.glean_labor_categories_from_file(
                uploaded_xlsx_file(R10_XLSX_PATH),
                sheet_name='foo'
            )
