# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0017_auto_20170104_1924'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='labor_category',
            field=models.TextField(db_index=True, db_column='labor_category'),
        ),
    ]
