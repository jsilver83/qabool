# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-06-20 12:13
from __future__ import unicode_literals

from django.db import migrations, models
import undergraduate_admission.media_handlers
import undergraduate_admission.validators


class Migration(migrations.Migration):

    dependencies = [
        ('undergraduate_admission', '0032_auto_20160618_1421'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='withdrawal_proof_letter',
            field=models.FileField(blank=True, null=True, upload_to=undergraduate_admission.media_handlers.upload_location_withdrawal_proof, validators=[undergraduate_admission.validators.validate_file_extension], verbose_name='Withdrawal Proof Letter'),
        ),
        migrations.AlterField(
            model_name='user',
            name='verification_status',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='Issues With Uploaded Docs'),
        ),
    ]
