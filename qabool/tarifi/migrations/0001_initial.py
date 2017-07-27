# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-07-27 13:13
from __future__ import unicode_literals

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('undergraduate_admission', '0005_auto_20170727_1603'),
    ]

    operations = [
        migrations.CreateModel(
            name='TarifiActivitySlot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slot_start_date', models.DateTimeField(null=True, verbose_name='Start Date')),
                ('slot_end_date', models.DateTimeField(null=True, verbose_name='End Date')),
                ('location_ar', models.CharField(max_length=600, null=True, verbose_name='Location (Arabic)')),
                ('location_en', models.CharField(max_length=600, null=True, verbose_name='Location (English)')),
                ('slots', models.PositiveSmallIntegerField(default=300, null=True, verbose_name='Slots')),
                ('type', models.CharField(choices=[('PREPARATION_COURSE', 'Preparation Course Attendance Date'), ('ENGLISH_PLACEMENT_TEST', 'English Placement Test Date'), ('ENGLISH_SPEAKING_TEST', 'English Speaking Test Date')], max_length=30, null=True, verbose_name='Slot Type')),
                ('description', models.CharField(blank=True, max_length=600, null=True, verbose_name='Description')),
                ('show', models.BooleanField(default=True, verbose_name='Show')),
                ('display_order', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Display Order')),
                ('semester', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tarifi_activities_dates', to='undergraduate_admission.AdmissionSemester', verbose_name='Semester')),
            ],
            options={
                'verbose_name_plural': 'Tarifi: Preparation Activity Slots',
            },
        ),
        migrations.CreateModel(
            name='TarifiUser',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='tarifi_user', serialize=False, to=settings.AUTH_USER_MODEL)),
                ('english_placement_test_score', models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)], verbose_name='English Placement Test Score')),
                ('english_speaking_test_score', models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)], verbose_name='English Speaking Test Score')),
                ('english_level', models.CharField(blank=True, max_length=20, null=True, verbose_name='English Level')),
                ('english_placement_test_date', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='students_in_placement_slot', to='tarifi.TarifiActivitySlot', verbose_name='English Placement Test Date')),
                ('english_speaking_test_date', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='students_in_speaking_slot', to='tarifi.TarifiActivitySlot', verbose_name='English Speaking Test Date')),
                ('preparation_course_attendance_date', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='students_in_course_slot', to='tarifi.TarifiActivitySlot', verbose_name='Preparation Course Attendance Date')),
            ],
        ),
    ]
