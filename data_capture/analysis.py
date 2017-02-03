import csv
import xlsxwriter

from django.http import HttpResponse
from django.utils import timezone

from .templatetags.analyze_contract import analyze_r10_row


class R10AnalysisExport:
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
        'Business Size',
        'SIN',
        'Site',
        'Exp',
        'Edu',
    ]

    def __init__(self, valid_rows):
        self.valid_rows = valid_rows

        context = {}
        self.analyzed_rows = []
        for row in valid_rows:
            analyzed_row = analyze_r10_row(context, row)
            self.analyzed_rows.append(analyzed_row)

    def _to_output_row(self, num, analyzed_row, valid_row):
        def pct_diff(a, b):
            return (a - b)/((a + b) / 2) * 100

        proposed_price = float(valid_row['price_including_iff'].value())

        # TODO: analyzed_row['severe'] and 'stddevs', and 'url'
        # are not included in the output because they are not in the template

        return [
            num + 1,
            analyzed_row['count'],
            valid_row['labor_category'].value(),
            valid_row['labor_category'].value(),
            valid_row['education_level'].value(),
            valid_row['min_years_experience'].value(),
            '',  # TODO: ? Most Common EDU
            '',  # TODO: ? Avg EXP
            proposed_price,
            float(analyzed_row['avg']),
            pct_diff(proposed_price, analyzed_row['avg']),
            proposed_price + analyzed_row['stddev'],
            pct_diff(proposed_price, analyzed_row['stddev']),
            '',  # TODO: Business Size - not used in analysis,
            valid_row['sin'].value(),
            '',  # TODO: Work site - not used in analysis
            valid_row['min_years_experience'].value(),  # duplicated value
            valid_row['education_level'].value(),  # duplicated value
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
