# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0018_auto_20170215_0031'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contract',
            old_name='labor_category',
            new_name='_labor_category',
        ),
    ]
