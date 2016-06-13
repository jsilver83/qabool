# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-06-04 18:03
from __future__ import unicode_literals

from django.db import migrations, models
import undergraduate_admission.media_handlers


class Migration(migrations.Migration):

    dependencies = [
        ('undergraduate_admission', '0012_auto_20160529_0750'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='lookup',
            options={'ordering': ['lookup_type', '-display_order']},
        ),
        migrations.AlterField(
            model_name='user',
            name='birth_certificate',
            field=models.FileField(blank=True, null=True, upload_to=undergraduate_admission.media_handlers.upload_location, validators=[undergraduate_admission.media_handlers.upload_location_birth], verbose_name='Birth Date Certificate'),
        ),
        migrations.AlterField(
            model_name='user',
            name='government_id_file',
            field=models.FileField(blank=True, null=True, upload_to=undergraduate_admission.media_handlers.upload_location, validators=[undergraduate_admission.media_handlers.upload_location_govid], verbose_name='Government ID File'),
        ),
        migrations.AlterField(
            model_name='user',
            name='mother_gov_id_file',
            field=models.FileField(blank=True, null=True, upload_to=undergraduate_admission.media_handlers.upload_location, validators=[undergraduate_admission.media_handlers.upload_location_mother_govid], verbose_name='Mother Government ID'),
        ),
        migrations.AlterField(
            model_name='user',
            name='passport_file',
            field=models.FileField(blank=True, null=True, upload_to=undergraduate_admission.media_handlers.upload_location, validators=[undergraduate_admission.media_handlers.upload_location_passport], verbose_name='Upload Passport'),
        ),
    ]