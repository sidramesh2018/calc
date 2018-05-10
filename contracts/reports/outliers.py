from contracts.models import Contract
from .base import BaseMetric


class Metric(BaseMetric):
    '''
    Find price outliers that seem way too expensive.

    For a more rigorous approach that uses anomaly
    detection, see:

        https://github.com/18F/calc-analysis/blob/master/contract-analysis/anomaly-detection.ipynb
    '''

    EDU_LEVEL = 'High School'

    EXPERIENCE_CAP = 5

    MIN_PRICE = 500

    def count(self) -> int:
        return Contract.objects.filter(
            education_level=Contract.get_education_code(
                self.EDU_LEVEL, raise_exception=True),
            min_years_experience__lt=self.EXPERIENCE_CAP,
            current_price__gt=self.MIN_PRICE,
        ).count()

    desc = f'''
    labor rates require a {EDU_LEVEL} education
    and under {EXPERIENCE_CAP} years
    of experience but pay over ${MIN_PRICE}
    per hour.
    '''

    footnote = f'''
    It's possible such pricing reflects *daily*
    rates rather *hourly* rates.
    '''
