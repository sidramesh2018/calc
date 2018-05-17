from contracts.models import Contract
from .base import BaseMetric


class Metric(BaseMetric):
    '''
    Find labor rates that are missing key data.
    '''

    def count(self) -> int:
        return Contract.objects.filter(
            education_level=None,
        ).count()

    desc = 'labor rates do not specify a minimum education level.'
