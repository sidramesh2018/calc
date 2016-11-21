# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('price_prediction', '0002_laborcategorylookup_start_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='FittedValuesByCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('labor_key', models.CharField(max_length=400)),
                ('fittedvalue', models.DecimalField(max_digits=12, decimal_places=12)),
                ('start_date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='PriceModels',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('labor_key', models.CharField(max_length=400)),
                ('model', models.BinaryField()),
            ],
        ),
    ]
