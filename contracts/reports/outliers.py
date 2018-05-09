from contracts.models import Contract


EDU_LEVEL = 'High School'

EXPERIENCE_CAP = 5

MIN_PRICE = 500


def count_outliers() -> int:
    return Contract.objects.filter(
        education_level=Contract.get_education_code(EDU_LEVEL, raise_exception=True),
        min_years_experience__lt=5,
        current_price__gt=500
    ).count()
