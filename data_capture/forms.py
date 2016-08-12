from django import forms

from .models import SubmittedPriceList
from .schedules import registry


class UploadWidget(forms.widgets.FileInput):
    def __init__(self, attrs=None, accept=(".xlsx", ".xls", ".csv"),
                 extra_instructions='XLS, XLSX, or CSV format, please.'):
        super().__init__(attrs=attrs)
        self.accept = accept
        self.extra_instructions = extra_instructions

    def render(self, name, value, attrs=None):
        final_attrs = {}
        if attrs:
            final_attrs.update(attrs)
        final_attrs['accept'] = ",".join(self.accept)

        id_for_label = final_attrs.get('id', '')

        return "\n".join([
            '<div class="upload">',
            '  %s' % super().render(name, value, final_attrs),
            '  <div class="upload-chooser">',
            '    <label for="%s">Choose file</label>' % id_for_label,
            '    <span class="js-only" aria-hidden="true">',
            '      or drag and drop here.',
            '    </span>',
            '    <span>%s</span>' % self.extra_instructions,
            '  </div>',
            '</div>'
        ])


class Step1Form(forms.Form):
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


class Step3Form(forms.ModelForm):
    class Meta:
        model = SubmittedPriceList
        fields = [
            'contract_number',
            'vendor_name',
            'is_small_business',
            'contractor_site',
            'contract_year',
            'contract_start',
            'contract_end',
        ]
