from django.core.exceptions import ValidationError


class Schedule70PriceList:
    title = 'IT Schedule 70'

    @classmethod
    def load_from_upload(cls, f):
        raise ValidationError(
            "TODO: Implement schedule 70 functionality!"
        )
