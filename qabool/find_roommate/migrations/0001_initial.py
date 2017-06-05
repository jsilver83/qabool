# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-06-01 14:46
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('undergraduate_admission', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HousingUser',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='housing_user', serialize=False, to=settings.AUTH_USER_MODEL)),
                ('facebook', models.URLField(blank=True, max_length=150, null=True, verbose_name='Facebook')),
                ('twitter', models.URLField(blank=True, max_length=150, null=True, verbose_name='Twitter')),
                ('sleeping', models.CharField(blank=True, max_length=150, null=True, verbose_name='Sleeping')),
                ('light', models.CharField(blank=True, max_length=150, null=True, verbose_name='Light')),
                ('room_temperature', models.CharField(blank=True, max_length=150, null=True, verbose_name='Room Temperature')),
                ('visits', models.CharField(blank=True, max_length=150, null=True, verbose_name='Visits')),
                ('interests_and_hobbies', models.TextField(blank=True, max_length=1000, null=True, verbose_name='Interests And Hobbies')),
                ('searchable', models.NullBooleanField(verbose_name='Searchable')),
            ],
        ),
    ]
