# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('price_prediction', '0018_newcontracts'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotNewContracts',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('year', models.DecimalField(decimal_places=2, max_digits=200)),
                ('price', models.DecimalField(decimal_places=2, max_digits=200)),
            ],
        ),
    ]
