# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('price_prediction', '0014_overallspread'),
    ]

    operations = [
        migrations.CreateModel(
            name='OverallCenter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('labor_category', models.CharField(max_length=400)),
                ('year', models.DecimalField(decimal_places=2, max_digits=200)),
                ('center', models.DecimalField(decimal_places=2, max_digits=200)),
            ],
        ),
    ]
