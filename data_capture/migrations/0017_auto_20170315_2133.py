# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import data_capture.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('data_capture', '0016_auto_20170306_1319'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttemptedPriceListSubmission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('uploaded_file_name', models.CharField(max_length=128, blank=True)),
                ('uploaded_file_content_type', models.CharField(max_length=128, blank=True)),
                ('valid_row_count', models.IntegerField(blank=True, null=True)),
                ('invalid_row_count', models.IntegerField(blank=True, null=True)),
                ('session_state', models.TextField()),
                ('submitter', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='HashedUploadedFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('hex_hash', models.CharField(max_length=64, unique=True, db_index=True)),
                ('contents', models.FileField(upload_to='data_capture_uploaded_files/', storage=data_capture.models.SlowpokeStorage())),
            ],
        ),
        migrations.CreateModel(
            name='SlowpokeStorageModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('data', models.BinaryField()),
                ('size', models.IntegerField()),
                ('name', models.CharField(max_length=128, unique=True, db_index=True)),
            ],
        ),
        migrations.AddField(
            model_name='attemptedpricelistsubmission',
            name='uploaded_file',
            field=models.ForeignKey(blank=True, null=True, to='data_capture.HashedUploadedFile'),
        ),
    ]
