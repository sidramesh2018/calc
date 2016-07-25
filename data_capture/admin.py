from django.contrib import admin
from django.db import models
from django import forms

from .schedules import registry
from .models import SubmittedPriceList, SubmittedPriceListRow


class SubmittedPriceListRowForm(forms.ModelForm):
    class Meta:
        model = SubmittedPriceListRow

        exclude = ('serialized_gleaned_data',)

        widgets = {
            'schedule': forms.widgets.Select()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['schedule'].widget.choices = registry.get_choices()


class SubmittedPriceListRowInline(admin.TabularInline):
    model = SubmittedPriceListRow

    exclude = ('contract_model_id',)

    formfield_overrides = {
        models.TextField: {'widget': forms.TextInput}
    }


@admin.register(SubmittedPriceList)
class SubmittedPriceListAdmin(admin.ModelAdmin):
    form = SubmittedPriceListRowForm

    inlines = [
        SubmittedPriceListRowInline
    ]
