import functools
import logging
import xlrd
import re

from django import forms
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string

from .base import BasePriceList, min_price_validator
from .coercers import strip_non_numeric, extract_min_education
from contracts.models import EDUCATION_CHOICES


DEFAULT_SHEET_NAME = '(3)Labor Categories'

EXAMPLE_SHEET_ROWS = [
    [
        r'SIN(s) PROPOSED',
        r'SERVICE PROPOSED (e.g. Job Title/Task)',
        r'MINIMUM EDUCATION/ CERTIFICATION LEVEL',
        r'MINIMUM YEARS OF EXPERIENCE',
        r'COMMERCIAL LIST PRICE (CPL) OR MARKET PRICES',
        r'UNIT OF ISSUE (e.g. Hour, Task, Sq ft)',
        r'MOST FAVORED CUSTOMER (MFC)',
        r'BEST  DISCOUNT OFFERED TO MFC (%)',
        r'MFC PRICE',
        r'GSA(%) DISCOUNT (exclusive of the .75% IFF)',
        r'PRICE OFFERED TO GSA (excluding IFF)',
        r'PRICE OFFERED TO GSA (including IFF)',
        r'QUANTITY/ VOLUME DISCOUNT',
    ],
    [
        r'132-51',
        r'Project Manager',
        r'Bachelors',
        r'5',
        r'$125',
        r'Hour',
        r'All Commercial Customers',
        r'7.00%',
        r'$123.99',
        r'10.00%',
        r'$110.99',
        r'$115.99',
        r'15.00%',
    ]
]

DEFAULT_FIELD_TITLE_MAP = {
    'sin': 'SIN(s) PROPOSED',
    'labor_category': 'SERVICE PROPOSED (e.g. Job Title/Task)',
    'education_level': 'MINIMUM EDUCATION/ CERTIFICATION LEVEL',
    'min_years_experience': 'MINIMUM YEARS OF EXPERIENCE',
    'commercial_list_price': 'COMMERCIAL LIST PRICE (CPL) OR MARKET PRICES',
    'unit_of_issue': 'UNIT OF ISSUE (e.g. Hour, Task, Sq ft)',
    'most_favored_customer': 'MOST FAVORED CUSTOMER (MFC)',
    'best_discount': 'BEST  DISCOUNT OFFERED TO MFC (%)',
    'mfc_price': 'MFC PRICE',
    'gsa_discount': 'GSA(%) DISCOUNT (exclusive of the .75% IFF)',
    'price_excluding_iff': 'PRICE OFFERED TO GSA (excluding IFF)',
    'price_including_iff': 'PRICE OFFERED TO GSA (including IFF)',
    'volume_discount': 'QUANTITY/ VOLUME DISCOUNT',
}

logger = logging.getLogger(__name__)


def safe_cell_str_value(sheet, rownum, colnum, coercer=None):
    val = ''

    try:
        val = sheet.cell_value(rownum, colnum)
    except IndexError:
        pass

    if coercer is not None:
        try:
            val = coercer(val)
        except ValueError:
            pass

    return str(val)


def generate_column_index_map(heading_row, field_title_map=None):
    def normalize(s):
        return re.sub(r'\s+', '', str(s).lower())

    def find_col(col_name):
        for idx, cell in enumerate(heading_row):
            if normalize(cell.value) == normalize(col_name):
                return idx
        raise ValidationError('Column heading "{}" was not found.'.format(
            col_name))

    if field_title_map is None:
        field_title_map = DEFAULT_FIELD_TITLE_MAP

    col_idx_map = {}
    for field, title in field_title_map.items():
        col_idx_map[field] = find_col(title)

    return col_idx_map


def find_header_row(sheet, row_threshold=50):
    first_col_heading = EXAMPLE_SHEET_ROWS[0][0]
    row_limit = min(sheet.nrows, row_threshold)

    for rx in range(row_limit):
        if sheet.cell_value(rx, 0) == first_col_heading:
            return rx

    raise ValidationError('Could not find Labor Categories price table.')


def glean_labor_categories_from_file(f, sheet_name=DEFAULT_SHEET_NAME):
    # TODO: I'm not sure how big these uploaded files can get. While
    # the labor categories price lists don't get that long, according to
    # user research interviews, *product* price lists can get really long;
    # and even though we're not interested in them, information about them
    # is embedded in the workbook, so the file could potentially get large.
    #
    # Unfortunately, it doesn't *seem* like xlrd supports file streaming.
    # Although it does support using memory-mapped files, so perhaps that's a
    # possibility.

    book = xlrd.open_workbook(file_contents=f.read())

    return glean_labor_categories_from_book(book, sheet_name)


def glean_labor_categories_from_book(book, sheet_name=DEFAULT_SHEET_NAME):
    if sheet_name not in book.sheet_names():
        raise ValidationError(
            'There is no sheet in the workbook called "%s".' % sheet_name
        )

    sheet = book.sheet_by_name(sheet_name)

    rownum = find_header_row(sheet) + 1  # add 1 to start on first data row

    cats = []

    heading_row = sheet.row(rownum - 1)

    col_idx_map = generate_column_index_map(heading_row)

    coercion_map = {
        'price_including_iff': strip_non_numeric,
        'min_years_experience': int,
        'education_level': extract_min_education,
        'commercial_list_price': strip_non_numeric,
        'mfc_price': strip_non_numeric,
        'price_excluding_iff': strip_non_numeric
    }

    while True:
        cval = functools.partial(safe_cell_str_value, sheet, rownum)

        sin = cval(col_idx_map['sin'])
        price_including_iff = cval(col_idx_map['price_including_iff'],
                                   coercer=strip_non_numeric)

        # We basically just keep going until we run into a row that
        # doesn't have a SIN or price including IFF.
        if not sin.strip() and not price_including_iff.strip():
            break

        cat = {}

        for field, col_idx in col_idx_map.items():
            coercer = coercion_map.get(field, None)
            cat[field] = cval(col_idx, coercer=coercer)

        cats.append(cat)

        rownum += 1

    return cats


class Schedule70Row(forms.Form):
    sin = forms.CharField(label="SIN(s) proposed")
    labor_category = forms.CharField(
        label="Service proposed (e.g. job title/task)"
    )
    education_level = forms.CharField(
        label="Minimum education / certification level",
    )
    min_years_experience = forms.IntegerField(
        label="Minimum years of experience"
    )
    price_including_iff = forms.DecimalField(
        label="Price offered to GSA (including IFF)",
        validators=[min_price_validator]
    )

    def clean_education_level(self):
        value = self.cleaned_data['education_level']

        values = [choice[1] for choice in EDUCATION_CHOICES]

        if value not in values:
            raise ValidationError('This field must contain one of the '
                                  'following values: %s' % (', '.join(values)))

        return value

    def contract_model_education_level(self):
        # Note that due to the way we've cleaned education_level, this
        # code is guaranteed to work.

        return [
            code for code, name in EDUCATION_CHOICES
            if name == self.cleaned_data['education_level']
        ][0]

    def contract_model_base_year_rate(self):
        return self.cleaned_data['price_including_iff']


class Schedule70PriceList(BasePriceList):
    title = 'IT Schedule 70'
    table_template = 'data_capture/price_list/tables/schedule_70.html'
    upload_example_template = ('data_capture/price_list/upload_examples/'
                               'schedule_70.html')
    upload_widget_extra_instructions = 'XLS or XLSX format, please.'

    def __init__(self, rows):
        super().__init__()

        self.rows = rows

        for row in self.rows:
            form = Schedule70Row(row)
            if form.is_valid():
                self.valid_rows.append(form)
            else:
                self.invalid_rows.append(form)

    def add_to_price_list(self, price_list):
        for row in self.valid_rows:
            price_list.add_row(
                labor_category=row.cleaned_data['labor_category'],
                education_level=row.contract_model_education_level(),
                min_years_experience=row.cleaned_data['min_years_experience'],
                base_year_rate=row.contract_model_base_year_rate(),
                sin=row.cleaned_data['sin']
            )

    def serialize(self):
        return self.rows

    def to_table(self):
        return render_to_string(self.table_template,
                                {'rows': self.valid_rows})

    def to_error_table(self):
        return render_to_string(self.table_template,
                                {'rows': self.invalid_rows})

    @classmethod
    def get_upload_example_context(cls):
        return {
            'sheet_name': DEFAULT_SHEET_NAME,
            'sheet_rows': EXAMPLE_SHEET_ROWS,
        }

    @classmethod
    def deserialize(cls, rows):
        return cls(rows)

    @classmethod
    def load_from_upload(cls, f):
        try:
            rows = glean_labor_categories_from_file(f)
            return Schedule70PriceList(rows)
        except ValidationError:
            raise
        except Exception as e:
            logger.info('Failed to glean data from %s: %s' % (f.name, e))

            raise ValidationError(
                "An error occurred when reading your Excel data."
            )
