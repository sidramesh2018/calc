from django import forms

from .models import NewPriceList, SubmittedPriceList
from .schedules import registry
from frontend.upload import UploadWidget
from frontend.date import SplitDateField


class Step1Form(forms.ModelForm):
    schedule = forms.ChoiceField(
        choices=registry.get_choices
    )
    class Meta:
        model = NewPriceList
        fields = [
            'contract_number',
            'vendor_name',
        ]

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
