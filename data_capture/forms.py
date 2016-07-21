from django import forms


SCHEDULE_CHOICES = [
    ('s70', 'IT Schedule 70'),
]


class Step1Form(forms.Form):
    schedule = forms.ChoiceField(
        choices=SCHEDULE_CHOICES
    )

    file = forms.FileField()

    def clean(self):
        cleaned_data = super().clean()
        schedule = cleaned_data.get('schedule')
        file = cleaned_data.get('file')

        if schedule and file:
            # TODO: Extract data from file and ensure there's some
            # data in it.

            raise forms.ValidationError(
                "The file you uploaded doesn't have any data we can "
                "glean from it."
            )
