from textwrap import dedent, fill
from django.core.management.base import BaseCommand

from contracts.reports import dupes, outliers


class Command(BaseCommand):
    help = '''
    Generate a report on the quality of CALC's data.
    '''

    def report(self, msg: str):
        self.stdout.write(fill(dedent(msg)).strip())
        self.stdout.write("\n")

    def handle(self, *args, **kwargs):
        self.report(f'''
            {dupes.count_duplicates()} labor rates
            share the same core fields
            ({', '.join(dupes.CORE_FIELDS)}) but
            differ along other axes.
        ''')

        self.report(f'''
            {outliers.count_outliers()} labor rates
            require a {outliers.EDU_LEVEL} education
            and under {outliers.EXPERIENCE_CAP} years
            of experience but pay over ${outliers.MIN_PRICE}
            per hour, which seems excessive. It's
            possible the price is actually their *daily*
            rate rather than their *hourly* rate.
        ''')
