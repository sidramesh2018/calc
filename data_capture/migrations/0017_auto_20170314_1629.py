# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils.timezone import utc
from django.conf import settings
import datetime


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('data_capture', '0016_uploadedfile'),
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
        migrations.AddField(
            model_name='uploadedfile',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2017, 3, 14, 16, 28, 55, 836540, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='uploadedfile',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2017, 3, 14, 16, 29, 1, 61902, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='uploadedfile',
            name='contents',
            field=models.FileField(upload_to='data_capture_uploaded_files/'),
        ),
        migrations.AddField(
            model_name='attemptedpricelistsubmission',
            name='uploaded_file',
            field=models.ForeignKey(blank=True, null=True, to='data_capture.UploadedFile'),
        ),
    ]
