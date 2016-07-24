from django.db import models
from django.contrib.auth.models import User

from contracts.models import Contract, EDUCATION_CHOICES
from .schedules import registry


class SubmittedPriceList(models.Model):
    # This is the equivalent of Contract.idv_piid.
    contract_number = models.CharField(
        max_length=128,
        help_text='This should be the full contract number, e.g. GS-XXX-XXXX.'
    )
    vendor_name = models.CharField(max_length=128)
    is_small_business = models.BooleanField()
    schedule = models.CharField(
        choices=registry.CHOICES,
        max_length=128
    )
    contractor_site = models.CharField(
        verbose_name='Worksite',
        choices=[
            ('Customer', 'Customer'),
            ('Contractor', 'Contractor'),
            ('Both', 'Both'),
        ],
        max_length=128
    )
    contract_year = models.IntegerField(null=True, blank=True)
    contract_start = models.DateField(
        null=True,
        blank=True,
        help_text='Use MM/DD/YY format, e.g. "10/25/06".'
    )
    contract_end = models.DateField(
        null=True,
        blank=True,
        help_text='Use MM/DD/YY format, e.g. "10/25/06".'
    )

    submitter = models.ForeignKey(User)
    is_approved = models.BooleanField(default=False)
    serialized_gleaned_data = models.TextField(
        help_text=(
            'The JSON-serialized data from the upload, including '
            'information about any rows that failed validation.'
        )
    )

    def add_row(self, **kwargs):
        row = SubmittedPriceListRow(**kwargs)
        self.rows.add(row)
        row.save()
        return row


class SubmittedPriceListRow(models.Model):
    labor_category = models.TextField()
    education_level = models.CharField(
        choices=EDUCATION_CHOICES, max_length=5, null=True,
        blank=True)
    min_years_experience = models.IntegerField()
    hourly_rate_year1 = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    sin = models.TextField(null=True, blank=True)

    price_list = models.ForeignKey(
        SubmittedPriceList,
        related_name='rows'
    )

    # If this row is represented in the contracts table, this will be
    # non-null.
    contract_model_id = models.ForeignKey(
        Contract,
        null=True,
        blank=True
    )
