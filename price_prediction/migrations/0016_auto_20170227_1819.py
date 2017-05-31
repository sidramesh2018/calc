# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('price_prediction', '0015_overallcenter'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompressedData',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('year', models.DecimalField(max_digits=200, decimal_places=2)),
                ('price', models.DecimalField(max_digits=200, decimal_places=2)),
            ],
        ),
        migrations.DeleteModel(
            name='OverallCenter',
        ),
        migrations.DeleteModel(
            name='OverallSpread',
        ),
    ]
