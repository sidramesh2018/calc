# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('price_prediction', '0003_fittedvaluesbycategory_pricemodels'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fittedvaluesbycategory',
            name='fittedvalue',
            field=models.DecimalField(max_digits=200, decimal_places=200),
        ),
    ]
