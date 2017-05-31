# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('price_prediction', '0016_auto_20170227_1819'),
    ]

    operations = [
        migrations.CreateModel(
            name='CALCOnlyData',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('year', models.DecimalField(decimal_places=2, max_digits=200)),
                ('price', models.DecimalField(decimal_places=2, max_digits=200)),
            ],
        ),
    ]
