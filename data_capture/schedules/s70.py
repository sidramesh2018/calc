from django.core.exceptions import ValidationError

from .base import BasePriceList


class Schedule70PriceList(BasePriceList):
    title = 'IT Schedule 70'

    @classmethod
    def load_from_upload(cls, f):
        raise ValidationError(
            "TODO: Implement schedule 70 functionality!"
        )
