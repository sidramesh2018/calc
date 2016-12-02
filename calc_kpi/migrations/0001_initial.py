# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ProposedContractingData',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('proposed_price', models.DecimalField(decimal_places=400, max_digits=400)),
                ('timestamp', models.DateField()),
            ],
        ),
    ]
