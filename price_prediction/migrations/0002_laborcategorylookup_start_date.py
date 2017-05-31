# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('price_prediction', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='laborcategorylookup',
            name='start_date',
            field=models.DateField(default=datetime.datetime(2016, 11, 17, 15, 31, 23, 64469, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
