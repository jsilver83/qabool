# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-06-09 09:29
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('undergraduate_admission', '0019_auto_20160609_1211'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='other_needs',
            new_name='disability_needs_notes',
        ),
    ]
