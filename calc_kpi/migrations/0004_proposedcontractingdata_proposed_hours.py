# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calc_kpi', '0003_auto_20161201_1652'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposedcontractingdata',
            name='proposed_hours',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
