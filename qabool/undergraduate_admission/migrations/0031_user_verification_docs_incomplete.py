# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-06-18 11:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('undergraduate_admission', '0030_verifystudent'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='verification_docs_incomplete',
            field=models.NullBooleanField(verbose_name='Uploaded docs are incomplete?'),
        ),
    ]