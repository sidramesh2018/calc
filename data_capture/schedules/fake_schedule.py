import csv
from io import StringIO
from django import forms
from django.core.exceptions import ValidationError


TITLE = 'Fake Schedule (for dev/debugging only)'

# TODO: Ideally this should pull from contracts.models.EDUCATION_CHOICES.
EDU_LEVELS = {
    'Associates': 'AA',
    'Bachelors': 'BA',
    'Masters': 'MA',
    'Ph.D': 'PHD'
}


def validate_education_level(value):
    values = EDU_LEVELS.keys()
    if value not in values:
        raise ValidationError('This field must contain one of the '
                              'following values: %s' % (', '.join(values)))


class FakeScheduleRow(forms.Form):
    sin = forms.CharField(label="SIN")
    service = forms.CharField(label="Service proposed")
    education = forms.CharField(
        label="Minimum education",
        validators=[validate_education_level]
    )
    years_experience = forms.IntegerField(
        label="Minimum years of experience"
    )
    price = forms.DecimalField(label="Price")


class FakeSchedulePriceList:
    def __init__(self, rows):
        self.rows = rows
        self.valid_rows = []
        self.invalid_rows = []

        for row in self.rows:
            form = FakeScheduleRow(row)
            if form.is_valid():
                self.valid_rows.append(form)
            else:
                self.invalid_rows.append(form)

    def is_empty(self):
        return not self.rows

    def serialize(self):
        return self.rows


def load(f):
    try:
        reader = csv.DictReader(StringIO(f.read().decode('utf-8')))
        return FakeSchedulePriceList([row for row in reader])
    except Exception:
        # TODO: Log the exception somewhere?
        raise ValidationError(
            'Weird problems occurred when reading your file.'
        )


def deserialize(rows):
    return FakeSchedulePriceList(rows)
