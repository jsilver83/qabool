# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-05-11 09:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('undergraduate_admission', '0035_auto_20170510_1635'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CutOff',
        ),
        migrations.AlterField(
            model_name='user',
            name='passport_number',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Passport Number'),
        ),
    ]