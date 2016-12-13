# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_capture', '0012_auto_20161207_1513'),
    ]

    operations = [
        migrations.AddField(
            model_name='submittedpricelist',
            name='uploaded_filename',
            field=models.CharField(max_length=128, help_text="Name of the file that was uploaded, as it was called on the uploader's system. For display purposes only.", default='unnamed'),
            preserve_default=False,
        ),
    ]
