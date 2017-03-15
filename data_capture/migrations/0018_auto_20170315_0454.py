# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import data_capture.models


class Migration(migrations.Migration):

    dependencies = [
        ('data_capture', '0017_auto_20170314_1629'),
    ]

    operations = [
        migrations.CreateModel(
            name='SlowpokeStorageModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('data', models.BinaryField()),
                ('size', models.IntegerField()),
                ('name', models.CharField(max_length=128, unique=True, db_index=True)),
            ],
        ),
        migrations.AlterField(
            model_name='uploadedfile',
            name='contents',
            field=models.FileField(upload_to='data_capture_uploaded_files/', storage=data_capture.models.SlowpokeStorage()),
        ),
    ]
