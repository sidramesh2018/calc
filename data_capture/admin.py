from django.contrib import admin
from django.db import models
from django import forms

from .schedules import registry
from .models import SubmittedPriceList, SubmittedPriceListRow


class SubmittedPriceListRowInline(admin.TabularInline):
    model = SubmittedPriceListRow

    exclude = ('contract_model_id',)

    formfield_overrides = {
        models.TextField: {'widget': forms.TextInput}
    }


@admin.register(SubmittedPriceList)
class SubmittedPriceListAdmin(admin.ModelAdmin):
    exclude = ('serialized_gleaned_data', 'schedule')

    readonly_fields = ('schedule_title',)

    inlines = [
        SubmittedPriceListRowInline
    ]

    def schedule_title(self, instance):
        return registry.get_class(instance.schedule).title

    schedule_title.short_description = 'Schedule'
