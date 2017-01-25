import xlrd

from django import forms
from django.core.exceptions import ValidationError

from .base import (BasePriceList, hourly_rates_only_validator,
                   min_price_validator)
from .spreadsheet_utils import generate_column_index_map


DEFAULT_SHEET_NAME = 'Service Pricing'

EXAMPLE_SHEET_ROWS = [
    [
        r'SIN(s) Proposed',
        r'Service Proposed (e.g. Labor Category or Job Title/Task)',
        r'Minimum Education / Certification Level',
        r'Minimum Years of Experience (cannot be a range)',
        r'Contractor or Customer Facility or Both',
        r'Domestic or Overseas',
        r'Commercial Price List (CPL) OR Market Prices',
        r'Unit of Issue (e.g. Hour, Task, Sq Ft)',
        r'Most Favored Commercial Customer (MFC)*',
        r'Discount Offered to Commercial MFC (%)',
        r'Commercial MFC Price',
        r'Discount Offered to GSA (off CPL or Market Prices) (%)',
        r'Price Offered to GSA (Excluding IFF)',
        r'Price Offered to GSA (including IFF)',
        r'Discount Offered to GSA (off MFC Prices) (%)',
    ],
    [
        r'123-1',
        r'Consultant II',
        r'Professional Certification',
        r'2',
        r'Both',
        r'Domestic Only',
        r'$100.00',
        r'hour',
        r'ABC Company',
        r'5.00%',
        r'$95.00',
        r'10.00%',
        r'$90.00',
        r'$90.68',
        r'5.26%',
    ],
]


DEFAULT_FIELD_TITLE_MAP = {
    'sin': 'SIN(s) Proposed',
    'labor_category': 'Service Proposed (e.g. Labor Category or Job Title/Task)',  # noqa
    'education_level': 'Minimum Education / Certification Level',
    'min_years_experience': 'Minimum Years of Experience (cannot be a range)',
    'unit_of_issue': 'Unit of Issue (e.g. Hour, Task, Sq Ft)',
    'price_including_iff': 'Price Offered to GSA (including IFF)',
}


# don't need find_header_row

def glean_labor_categories_from_file(f, sheet_name=DEFAULT_SHEET_NAME):
    book = xlrd.open_workbook(file_contents=f.read())
    return glean_labor_categories_from_book(book, sheet_name)


def glean_labor_categories_from_book(book, sheet_name=DEFAULT_SHEET_NAME):
    if sheet_name not in book.sheet_names():
        raise ValidationError(
            'There is no sheet in the workbook called "%s".' % sheet_name
        )

    sheet = book.sheet_by_name(sheet_name)

    cats = []

    heading_row = sheet.row(0)

    col_idx_map = generate_column_index_map(heading_row,
                                            DEFAULT_FIELD_TITLE_MAP)

    print(col_idx_map)


class Region10PriceList(BasePriceList):
    pass


class Region10PriceListRow(forms.Form):
    sin = forms.CharField(label='SIN(s) Proposed')
    labor_category = forms.CharField(
        label="Service Proposed (e.g. Labor Category or Job Title/Task)"
    )
    education_level = forms.CharField(
        label="Minimum Education / Certification Level"
    )
    min_years_experience = forms.IntegerField(
        label="Minimum Years of Experience (cannot be a range)"
    )
    unit_of_issue = forms.CharField(
        label="Unit of issue",
        validators=[hourly_rates_only_validator]
    )
    price_including_iff = forms.DecimalField(
        label='Price Offered to GSA (including IFF)',
        validators=[min_price_validator]
    )
