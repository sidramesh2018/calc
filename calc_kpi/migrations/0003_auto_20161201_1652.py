# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calc_kpi', '0002_auto_20161201_1637'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposedcontractingdata',
            name='proposed_price',
            field=models.DecimalField(max_digits=100, decimal_places=4),
        ),
    ]
