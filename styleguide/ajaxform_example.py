from django import forms

from data_capture import ajaxform
from data_capture.forms import UploadWidget


class ExampleForm(forms.Form):
    question = forms.IntegerField(label='What is 2+2?')

    file = forms.FileField(widget=UploadWidget(
        accept=('.csv',),
        extra_instructions="CSV only, please."
    ))

    def clean_question(self):
        data = self.cleaned_data['question']
        if data != 4:
            raise forms.ValidationError('2 + 2 is not %d!' % data)
        return data


def create_template_context(ajaxform_form=None):
    if ajaxform_form is None:
        ajaxform_form = ExampleForm()

    return {'ajaxform_form': ajaxform_form}


def view(request):
    form = None

    if request.method == 'POST':
        form = ExampleForm(request.POST, request.FILES)

        if form.is_valid():
            return ajaxform.redirect(request, 'styleguide:index')

    return ajaxform.render(
        request,
        context=create_template_context(ajaxform_form=form),
        template_name='styleguide_ajaxform.html',
        ajax_template_name='styleguide_ajaxform_example.html'
    )
