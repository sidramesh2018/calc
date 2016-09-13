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


class Step3Form(forms.Form):
    file = forms.FileField(widget=UploadWidget())

    def __init__(self, *args, **kwargs):
        self.schedule = kwargs.pop('schedule')
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')

        if file:
            gleaned_data = registry.smart_load_from_upload(self.schedule,
                                                           file)

            if gleaned_data.is_empty():
                raise forms.ValidationError(
                    "The file you uploaded doesn't have any data we can "
                    "glean from it."
                )

            cleaned_data['gleaned_data'] = gleaned_data

        return cleaned_data
