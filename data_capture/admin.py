from django.contrib import admin
from django.db import models
from django import forms

from .models import SubmittedPriceList, SubmittedPriceListRow


class SubmittedPriceListRowInline(admin.TabularInline):
    model = SubmittedPriceListRow

    exclude = ('contract_model_id',)

    formfield_overrides = {
        models.TextField: {'widget': forms.TextInput}
    }


@admin.register(SubmittedPriceList)
class SubmittedPriceListAdmin(admin.ModelAdmin):
    exclude = ('serialized_gleaned_data',)

    inlines = [
        SubmittedPriceListRowInline
    ]
