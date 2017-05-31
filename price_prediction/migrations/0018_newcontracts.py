# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('price_prediction', '0017_calconlydata'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewContracts',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('year', models.DecimalField(max_digits=200, decimal_places=2)),
                ('price', models.DecimalField(max_digits=200, decimal_places=2)),
            ],
        ),
    ]
