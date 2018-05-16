# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2018-05-16 12:12
from __future__ import unicode_literals

from django.db import migrations, models
import undergraduate_admission.media_handlers
import undergraduate_admission.validators


class Migration(migrations.Migration):

    dependencies = [
        ('undergraduate_admission', '0006_auto_20180404_1736'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tarifireceptiondate',
            options={'ordering': ['slot_start_date'], 'verbose_name_plural': 'Orientation Week: Schedule'},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'user', 'verbose_name_plural': 'Users: Change Password'},
        ),
        migrations.AddField(
            model_name='user',
            name='bank_account',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Bank Account'),
        ),
        migrations.AddField(
            model_name='user',
            name='bank_account_identification_file',
            field=models.FileField(blank=True, null=True, upload_to=undergraduate_admission.media_handlers.upload_bank_account_identification, validators=[undergraduate_admission.validators.validate_file_extension], verbose_name='Bank Account Identification File'),
        ),
        migrations.AddField(
            model_name='user',
            name='bank_name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Bank Name'),
        ),
    ]
