# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_capture', '0015_auto_20170131_1815'),
    ]

    operations = [
        migrations.CreateModel(
            name='UploadedFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('hex_hash', models.CharField(max_length=64, unique=True, db_index=True)),
                ('contents', models.FileField(upload_to='')),
            ],
        ),
    ]
