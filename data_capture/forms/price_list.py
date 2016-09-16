from django import forms

from ..models import SubmittedPriceList
from ..schedules import registry
from frontend.upload import UploadWidget
from frontend.date import SplitDateField
from frontend.radio import UswdsRadioSelect


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

    def clean(self):
        cleaned_data = super().clean()
        schedule = cleaned_data.get('schedule')
        if schedule:
            cleaned_data['schedule_class'] = registry.get_class(schedule)
        return cleaned_data


class Step2Form(forms.ModelForm):
    is_small_business = forms.ChoiceField(
        label='Business size',
        choices=[
            (True, 'This is a small business.'),
            (False, 'This is not a small business.'),
        ],
        widget=UswdsRadioSelect,
    )
    contractor_site = forms.ChoiceField(
        label='Worksite',
        choices=SubmittedPriceList.CONTRACTOR_SITE_CHOICES,
        widget=UswdsRadioSelect,
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
        widget=UswdsRadioSelect,
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
    file = forms.FileField(widget=UploadWidget())

    def __init__(self, *args, **kwargs):
        '''
        This constructor requires `schedule` to be passed in as a
        keyword argument. It should be a string referring to the
        fully-qualified class name for an entry in the schedule
        registry, e.g.
        "data_capture.schedules.fake_schedule.FakeSchedulePriceList".
        '''

        self.schedule = kwargs.pop('schedule')
        self.schedule_class = registry.get_class(self.schedule)

        super().__init__(*args, **kwargs)

        extra = self.schedule_class.upload_widget_extra_instructions
        if extra is not None:
            self.fields['file'].widget.extra_instructions = extra

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
