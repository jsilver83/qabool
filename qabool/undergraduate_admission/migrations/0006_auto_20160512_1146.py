# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-12 08:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('undergraduate_admission', '0005_auto_20160512_1142'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agreementitem',
            name='show',
            field=models.BooleanField(default=True, verbose_name='Show'),
        ),
        migrations.AlterField(
            model_name='city',
            name='show',
            field=models.BooleanField(default=True, verbose_name='Show'),
        ),
        migrations.AlterField(
            model_name='distinguishedstudent',
            name='attended',
            field=models.BooleanField(default=True, verbose_name='Attended'),
        ),
        migrations.AlterField(
            model_name='graduationyear',
            name='show',
            field=models.BooleanField(default=True, verbose_name='Show'),
        ),
        migrations.AlterField(
            model_name='nationality',
            name='show',
            field=models.BooleanField(default=True, verbose_name='Show'),
        ),
    ]
