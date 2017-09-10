# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-09-10 12:36
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tarifi', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BoxesForIDRanges',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_kfupm_id', models.PositiveIntegerField(null=True, verbose_name='From KFUPM ID')),
                ('to_kfupm_id', models.PositiveIntegerField(null=True, verbose_name='To KFUPM ID')),
                ('box_no', models.CharField(max_length=20, null=True, verbose_name='Box No')),
            ],
        ),
        migrations.CreateModel(
            name='StudentIssue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kfupm_id', models.PositiveIntegerField(null=True, verbose_name='KFUPM ID')),
                ('issues', models.CharField(max_length=500, null=True, verbose_name='Box No')),
                ('show', models.BooleanField(default=True, verbose_name='Show')),
            ],
        ),
        migrations.AlterModelOptions(
            name='tarifiactivityslot',
            options={'ordering': ['display_order', 'slot_start_date'], 'verbose_name_plural': 'Tarifi: Preparation Activity Slots'},
        ),
        migrations.RemoveField(
            model_name='tarifiuser',
            name='english_placement_test_date',
        ),
        migrations.RemoveField(
            model_name='tarifiuser',
            name='english_speaking_test_date',
        ),
        migrations.RemoveField(
            model_name='tarifiuser',
            name='preparation_course_attendance_date',
        ),
        migrations.AddField(
            model_name='tarifiactivityslot',
            name='attender',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assigned_slots', to=settings.AUTH_USER_MODEL, verbose_name='Attender'),
        ),
        migrations.AddField(
            model_name='tarifiuser',
            name='creation_date',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Creation Date'),
        ),
        migrations.AddField(
            model_name='tarifiuser',
            name='english_placement_test_slot',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='students_in_placement_slot', to='tarifi.TarifiActivitySlot', verbose_name='English Placement Test Slot'),
        ),
        migrations.AddField(
            model_name='tarifiuser',
            name='english_speaking_test_slot',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='students_in_speaking_slot', to='tarifi.TarifiActivitySlot', verbose_name='English Speaking Test Slot'),
        ),
        migrations.AddField(
            model_name='tarifiuser',
            name='english_speaking_test_start_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='English Speaking Test Time'),
        ),
        migrations.AddField(
            model_name='tarifiuser',
            name='preparation_course_attendance',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Preparation Course Attendance Date'),
        ),
        migrations.AddField(
            model_name='tarifiuser',
            name='preparation_course_attended_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='attended_students', to=settings.AUTH_USER_MODEL, verbose_name='Preparation Course Attended By'),
        ),
        migrations.AddField(
            model_name='tarifiuser',
            name='preparation_course_slot',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='students_in_course_slot', to='tarifi.TarifiActivitySlot', verbose_name='Preparation Course Slot'),
        ),
        migrations.AddField(
            model_name='tarifiuser',
            name='received_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='students_received', to=settings.AUTH_USER_MODEL, verbose_name='Received By'),
        ),
        migrations.AddField(
            model_name='tarifiuser',
            name='updated_on',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='Updated On'),
        ),
    ]