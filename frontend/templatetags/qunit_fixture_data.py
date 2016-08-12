import json
from django import template
from django import forms

from data_capture.forms import UploadWidget


register = template.Library()


class UploadTestsForm(forms.Form):
    file = forms.FileField(widget=UploadWidget(
        accept=('.csv', 'application/test')
    ))


@register.simple_tag
def qunit_fixture_data_json():
    data = {
        'UPLOAD_TESTS_HTML': str(UploadTestsForm()['file'])
    }

    return json.dumps(data)
