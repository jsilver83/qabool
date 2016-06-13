# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-06-13 08:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('undergraduate_admission', '0025_auto_20160612_1810'),
    ]

    operations = [
        migrations.CreateModel(
            name='Aux1To100',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('counter', models.PositiveIntegerField(blank=True, null=True, verbose_name='Counter')),
            ],
        ),
        migrations.CreateModel(
            name='KFUPMIDsPool',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kfupm_id', models.PositiveIntegerField(blank=True, null=True, unique=True, verbose_name='KFUPM ID')),
            ],
        ),
        migrations.AddField(
            model_name='admissionsemester',
            name='cutoff_point',
            field=models.FloatField(blank=True, null=True, verbose_name='Cutoff Point'),
        ),
        migrations.AddField(
            model_name='user',
            name='is_disabled',
            field=models.BooleanField(default=False, help_text='This will let us help you better and will not affect your acceptance chances.', verbose_name='Do you have any disabilities?'),
        ),
        migrations.AddField(
            model_name='user',
            name='is_diseased',
            field=models.BooleanField(default=False, help_text='This will let us help you better and will not affect your acceptance chances.', verbose_name='Do you have any chronic diseases?'),
        ),
        migrations.AddField(
            model_name='kfupmidspool',
            name='semester',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='semester_ids', to='undergraduate_admission.AdmissionSemester', verbose_name='Admission Semester'),
        ),
    ]
