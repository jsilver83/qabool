# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2018-06-10 05:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('undergraduate_admission', '0009_auto_20180523_1447'),
    ]

    operations = [
        migrations.AddField(
            model_name='graduationyear',
            name='type',
            field=models.CharField(choices=[('CURRENT-YEAR', 'Current high school graduation year'), ('LAST-YEAR', 'Previous high school graduation year'), ('OLD-HS', 'Old High school graduation year')], default='OLD-HS', max_length=10, null=True, verbose_name='Type'),
        ),
        migrations.AddField(
            model_name='user',
            name='yesser_high_school_data_dump',
            field=models.TextField(blank=True, null=True, verbose_name='Fetched Yesser High School Data Dump'),
        ),
        migrations.AddField(
            model_name='user',
            name='yesser_qudrat_data_dump',
            field=models.TextField(blank=True, null=True, verbose_name='Fetched Yesser Qudrat Data Dump'),
        ),
        migrations.AddField(
            model_name='user',
            name='yesser_tahsili_data_dump',
            field=models.TextField(blank=True, null=True, verbose_name='Fetched Yesser Tahsili Data Dump'),
        ),
    ]