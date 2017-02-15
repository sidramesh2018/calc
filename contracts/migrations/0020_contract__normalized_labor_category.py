# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0019_auto_20170215_0032'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='_normalized_labor_category',
            field=models.TextField(db_index=True, default=''),
            preserve_default=False,
        ),
    ]
