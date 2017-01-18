from django import forms
from django.shortcuts import render

from frontend.upload import UploadWidget
from frontend.steps import StepsWidget
from . import ajaxform_example, date_example, radio_checkbox_example


def get_degraded_upload_widget():
    class MyForm(forms.Form):
        file = forms.FileField(widget=UploadWidget(degraded=True))

    return MyForm()['file']


def get_existing_filename_upload_form():
    class MyForm(forms.Form):
        js = forms.FileField(widget=UploadWidget(
            required=False,
            existing_filename='boop.csv',
        ))
        no_js = forms.FileField(widget=UploadWidget(
            degraded=True,
            required=False,
            existing_filename='boop.csv',
        ))

    return MyForm()


def index(request):
    ctx = {
        'degraded_upload_widget': get_degraded_upload_widget(),
        'existing_filename_upload_form': get_existing_filename_upload_form(),
        'steps_widget': StepsWidget(
            labels=('Upload data', 'Validate data', 'Recover costs'),
            current=2
        )
    }
    ctx.update(ajaxform_example.create_template_context())
    ctx.update(date_example.create_template_context())
    ctx.update(radio_checkbox_example.create_template_context())

    return render(request, 'styleguide.html', ctx)
