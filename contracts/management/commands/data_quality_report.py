from typing import List
from django.core.management.base import BaseCommand

from contracts.reports.base import BaseMetric
from contracts.reports import dupes, outliers, incomplete, expired

ALL_METRICS: List[BaseMetric] = [
    dupes.Metric(),
    outliers.Metric(),
    incomplete.Metric(),
    expired.Metric(),
]


class Command(BaseCommand):
    help = '''
    Generate a report on the quality of CALC's data.
    '''

    def report(self, metric: BaseMetric):
        msg = f"{metric.count()} {metric.desc_text}"
        self.stdout.write(msg)
        self.stdout.write("\n")

    def handle(self, *args, **kwargs):
        for metric in ALL_METRICS:
            self.report(metric)
