from django import forms
from django.shortcuts import render
from django.contrib import messages

from frontend.radio import UswdsRadioSelect


class ExampleForm(forms.Form):
    choices = forms.ChoiceField(
        widget=UswdsRadioSelect,
        choices=(
            ('1', 'First'),
            ('2', 'Second'),
        )
    )


def create_template_context(radio_form=None):
    if radio_form is None:
        radio_form = ExampleForm()

    return {'radio_form': radio_form}


def view(request):
    form = None

    if request.method == 'POST':
        form = ExampleForm(request.POST)

        if form.is_valid():
            messages.add_message(
                request, messages.SUCCESS,
                "You chose option #{}!".format(form.cleaned_data['choices'])
            )
        else:
            messages.add_message(
                request, messages.ERROR,
                'Uh oh. Please correct the error(s) below and try again.'
            )

    return render(
        request,
        'styleguide_radio.html',
        create_template_context(radio_form=form),
    )
