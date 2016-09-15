from django import forms
from django.utils.html import format_html


class UswdsRadioChoiceInput(forms.widgets.RadioChoiceInput):
    '''
    A widget for a USWDS-style radio input.

    This is basically just like Django's standard radio input, except
    the <label> is a sibling of its <input>, rather than its parent.
    '''

    def render(self, name=None, value=None, attrs=None):
        # This is mostly just a copy-paste of our superclass method, it
        # just tweaks the HTML structure to be USWDS-friendly.

        if self.id_for_label:
            label_for = format_html(' for="{}"', self.id_for_label)
        else:
            label_for = ''
        attrs = dict(self.attrs, **attrs) if attrs else self.attrs
        return format_html(
            '{}<label{}>{}</label>', self.tag(attrs), label_for,
            self.choice_label,
        )


class UswdsRadioFieldRenderer(forms.widgets.ChoiceFieldRenderer):
    choice_input_class = UswdsRadioChoiceInput


class UswdsRadioSelect(forms.widgets.RadioSelect):
    renderer = UswdsRadioFieldRenderer
