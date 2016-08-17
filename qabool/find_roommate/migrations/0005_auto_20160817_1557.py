# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-08-17 12:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('find_roommate', '0004_auto_20160811_0638'),
    ]

    operations = [
        migrations.AlterField(
            model_name='housinguser',
            name='light',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='Light'),
        ),
        migrations.AlterField(
            model_name='housinguser',
            name='room_temperature',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='Room Temperature'),
        ),
        migrations.AlterField(
            model_name='housinguser',
            name='sleeping',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='Sleeping'),
        ),
        migrations.AlterField(
            model_name='housinguser',
            name='visits',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='Visits'),
        ),
    ]
