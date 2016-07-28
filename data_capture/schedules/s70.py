import functools
import logging
from django.core.exceptions import ValidationError
import xlrd

from .base import BasePriceList


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


def glean_labor_categories_from_file(f, sheet_name='(3)Labor Categories'):
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

    if sheet_name not in book.sheet_names():
        raise ValidationError(
            'There is no sheet in the workbook called "%s".' % sheet_name
        )

    sheet = book.sheet_by_name(sheet_name)

    rownum = 3
    cats = []

    while True:
        sin = sheet.cell_value(rownum, 0)

        # We basically just keep going until we run into a row that
        # doesn't have a SIN.
        if not sin.strip():
            break

        cval = functools.partial(safe_cell_str_value, sheet, rownum)

        cat = {}
        cat['sin'] = sin
        cat['labor_category'] = cval(1)
        cat['education_level'] = cval(2)
        cat['min_years_experience'] = cval(3, coercer=int)
        cat['commercial_list_price'] = cval(4)
        cat['unit_of_issue'] = cval(5)
        cat['most_favored_customer'] = cval(6)
        cat['best_discount'] = cval(7)
        cat['mfc_price'] = cval(8)
        cat['gsa_discount'] = cval(9)
        cat['price_excluding_iff'] = cval(10)
        cat['price_including_iff'] = cval(11)
        cat['volume_discount'] = cval(12)
        cats.append(cat)

        rownum += 1

    return cats


class Schedule70PriceList(BasePriceList):
    title = 'IT Schedule 70'

    @classmethod
    def load_from_upload(cls, f):
        try:
            cats = glean_labor_categories_from_file(f)
        except ValidationError:
            raise
        except Exception as e:
            logger.info('Failed to glean data from %s: %s' % (f.name, e))

            raise ValidationError(
                "An error occurred when reading your Excel data."
            )
