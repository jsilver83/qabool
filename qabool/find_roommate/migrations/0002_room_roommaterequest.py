# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-08-01 17:54
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('find_roommate', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('building', models.CharField(max_length=20, null=True, verbose_name='Building')),
                ('room', models.CharField(max_length=20, null=True, verbose_name='Room')),
                ('available', models.BooleanField(default=True, verbose_name='Available')),
            ],
        ),
        migrations.CreateModel(
            name='RoommateRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(blank=True, choices=[('A', 'Accepted'), ('W2', 'Requested Withdrawn'), ('R', 'Rejected'), ('P', 'Pending'), ('E', 'Expired'), ('W1', 'Requester Withdrawn')], max_length=10, null=True, verbose_name='Status')),
                ('request_date', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Request Date')),
                ('updated_on', models.DateTimeField(auto_now=True, null=True, verbose_name='Updated On')),
                ('assigned_room', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='residing', to='find_roommate.Room', verbose_name='Assigned Room')),
                ('requested_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='roommate_request_received', to=settings.AUTH_USER_MODEL)),
                ('requesting_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='roommate_request_sent', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]