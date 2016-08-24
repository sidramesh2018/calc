from django import forms

from .models import SubmittedPriceList
from .schedules import registry
from frontend.upload import UploadWidget
from frontend.date import SplitDateField


class Step1Form(forms.Form):
    schedule = forms.ChoiceField(
        choices=registry.get_choices
    )
    contract_number = forms.CharField(
        max_length=128,
        help_text='This should be the full contract number, e.g. GS-XXX-XXXX.'
    )
    vendor_name = forms.CharField(max_length=128)


class Step2Form(forms.ModelForm):
    is_small_business = forms.ChoiceField(
        label='Business size',
        choices=[
            (True, 'Small business'),
            (False, 'Not a small business'),
        ],
        widget=forms.widgets.RadioSelect,
    )

    contract_start = SplitDateField(required=False)
    contract_end = SplitDateField(required=False)

    class Meta:
        model = SubmittedPriceList
        fields = [
            'is_small_business',
            'contractor_site',
            'contract_start',
            'contract_end',
            'contract_year',
        ]
        widgets = {
            'contract_number': forms.HiddenInput(),
            'vendor_name': forms.HiddenInput(),
            'schedule': forms.HiddenInput(),
        }

class Step3Form(forms.Form):
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
