import csv
import xlsxwriter

from django.http import HttpResponse
from django.utils import timezone

COMPARABLES_NOT_FOUND = 'Error: Comparables not found'


def pct_diff(a, b):
    return (a - b)/((a + b) / 2) * 100


class AnalysisExport:
    output_headers = [
        '#',
        'No of Comps',
        'Vendor Labor Category',
        'Search Labor Category',
        'Proposed Edu',
        'Proposed Exp',
        'Most Common EDU',
        'Avg EXP',
        'Offered Hourly Price',
        'Average Price',
        '% Diff from Average',
        '+ 1 Standard Deviation',
        '% Diff from +1 Standard Deviation',
        'SIN',
        'Site',
        'Exp Comparable Search Criteria',
        'Edu Comparable Search Criteria',
        'Outside 1 Standard Deviation',
    ]

    def __init__(self, rows):
        self.valid_rows = rows
        self.analyzed_rows = [row['analysis'] for row in rows]

    def _to_output_row(self, num, analyzed_row, valid_row):
        # NOTE: analyzed_row['severe'] and 'url'
        # are not included in the output because they are not in the template
        proposed_price = float(valid_row['price'])

        # Use presence of 'count' as a proxy to determine if the
        # analyzed_row is populated.
        if 'count' not in analyzed_row:
            # If not, then return a mostly empty line
            return [
                num + 1,
                0,
                valid_row['labor_category'],
                COMPARABLES_NOT_FOUND,
                valid_row['education_level'],
                valid_row['min_years_experience'],
                '',
                '',
                proposed_price,
                '',
                '',
                '',
                '',
                valid_row['sin'],
            ]

        outside_one_std_dev = 'Yes' if analyzed_row['stddevs'] > 1 else 'No'

        return [
            num + 1,
            analyzed_row['count'],
            valid_row['labor_category'],
            valid_row['labor_category'],
            valid_row['education_level'],
            valid_row['min_years_experience'],
            '',  # TODO: ? Most Common EDU
            '',  # TODO: ? Avg EXP
            proposed_price,
            float(analyzed_row['avg']),
            pct_diff(proposed_price, analyzed_row['avg']),
            proposed_price + analyzed_row['stddev'],
            pct_diff(proposed_price, analyzed_row['stddev']),
            valid_row['sin'],
            '',  # TODO: Work site - not used in analysis
            '',  # TODO: ? Exp Comparable Search Criteria
            '',  # TODO: ? Edu Comparable Search Criteria
            outside_one_std_dev,
        ]

    def to_csv(self, filename="analysis.csv"):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(
            filename)

        writer = csv.writer(response)
        writer.writerow(self.output_headers)

        for idx, (analyzed_row, row) in enumerate(zip(
                self.analyzed_rows, self.valid_rows)):
            writer.writerow(self._to_output_row(idx, analyzed_row, row))

        return response

    def to_xlsx(self, filename="analysis.xlsx"):
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-'
                         'officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(
            filename)

        workbook = xlsxwriter.Workbook(response)
        worksheet = workbook.add_worksheet()

        def write_row(row_idx, values):
            for col_idx, val in enumerate(values):
                worksheet.write(row_idx, col_idx, val)

        worksheet.write(0, 0, 'Price Analysis Data as of {}'.format(
            timezone.now().date()))

        write_row(1, self.output_headers)

        row_offset = 2  # sheet heading + table header row

        for row_idx, (analyzed_row, row) in enumerate(zip(
                self.analyzed_rows, self.valid_rows)):
            out_row = self._to_output_row(row_idx, analyzed_row, row)
            write_row(row_idx + row_offset, out_row)

        workbook.close()

        return response
