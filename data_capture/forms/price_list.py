from django import forms

from ..models import SubmittedPriceList
from ..schedules import registry
from frontend.upload import UploadWidget
from frontend.date import SplitDateField


class Step1Form(forms.ModelForm):
    schedule = forms.ChoiceField(
        choices=registry.get_choices
    )

    class Meta:
        model = SubmittedPriceList
        fields = [
            'schedule',
            'contract_number',
            'vendor_name',
        ]


class Step2Form(forms.ModelForm):
    is_small_business = forms.ChoiceField(
        label='Business size',
        choices=[
            (True, 'This is a small business.'),
            (False, 'This is not a small business.'),
        ],
        widget=forms.widgets.RadioSelect,
    )
    contractor_site = forms.ChoiceField(
        label='Worksite',
        choices=[
            ('Customer', 'Customer/Offsite'),
            ('Contractor', 'Contractor/Onsite'),
            ('Both', 'Both'),
        ],
        widget=forms.widgets.RadioSelect,
    )
    contract_start = SplitDateField(required=False)
    contract_end = SplitDateField(required=False)

    contract_year = forms.ChoiceField(
        label='Contract year',
        choices=[
            (1, '1'),
            (2, '2'),
            (3, '3'),
            (4, '4'),
            (5, '5'),
        ],
        widget=forms.widgets.RadioSelect,
    )


    class Meta:
        model = SubmittedPriceList
        fields = [
            'is_small_business',
            'contractor_site',
            'contract_start',
            'contract_end',
            'contract_year',
        ]


class Step3Form(forms.Form):
    # TODO: We should figure out a way of getting rid of this field, since
    # we're not actually asking the user for it anymore.

    schedule = forms.ChoiceField(
        choices=registry.get_choices
    )

    file = forms.FileField(widget=UploadWidget())

    def clean(self):
        cleaned_data = super().clean()
        schedule = cleaned_data.get('schedule')
        file = cleaned_data.get('file')

        if schedule and file:
            gleaned_data = registry.smart_load_from_upload(schedule, file)

            if gleaned_data.is_empty():
                raise forms.ValidationError(
                    "The file you uploaded doesn't have any data we can "
                    "glean from it."
                )

            cleaned_data['gleaned_data'] = gleaned_data

        return cleaned_data
