from textwrap import dedent, fill
from typing import List
from django.core.management.base import BaseCommand

from contracts.reports.base import BaseMetric
from contracts.reports import dupes, outliers, incomplete

ALL_METRICS: List[BaseMetric] = [
    dupes.Metric(),
    outliers.Metric(),
    incomplete.Metric(),
]


class Command(BaseCommand):
    help = '''
    Generate a report on the quality of CALC's data.
    '''

    def report(self, metric: BaseMetric):
        count = metric.count()
        msg = metric.describe(count)
        self.stdout.write(fill(dedent(msg)).strip())
        self.stdout.write("\n")

    def handle(self, *args, **kwargs):
        for metric in ALL_METRICS:
            self.report(metric)
