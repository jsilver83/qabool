# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-05-10 13:24
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('undergraduate_admission', '0039_auto_20170501_1435'),
    ]

    operations = [
        migrations.CreateModel(
            name='TarifiReceptionDate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reception_date', models.CharField(max_length=600, null=True, verbose_name='Reception Date')),
                ('slots', models.PositiveSmallIntegerField(default=300, null=True, verbose_name='Slots')),
                ('slot_start_date', models.DateTimeField(null=True, verbose_name='Start Date')),
                ('slot_end_date', models.DateTimeField(null=True, verbose_name='End Date')),
            ],
            options={
                'verbose_name_plural': 'Admission: Tarifi Reception Dates',
            },
        ),
        migrations.AlterModelOptions(
            name='admissionsemester',
            options={'verbose_name': 'Admission Semester', 'verbose_name_plural': 'Admission: Admission Semesters'},
        ),
        migrations.AlterModelOptions(
            name='agreement',
            options={'verbose_name_plural': 'Admission and Student Affairs: Agreements'},
        ),
        migrations.AlterModelOptions(
            name='agreementitem',
            options={'ordering': ['agreement', '-display_order'], 'verbose_name_plural': 'Admission and Student Affairs: Agreement Items'},
        ),
        migrations.AlterModelOptions(
            name='city',
            options={'ordering': ['-display_order'], 'verbose_name_plural': 'Admission: Cities'},
        ),
        migrations.AlterModelOptions(
            name='deniedstudent',
            options={'verbose_name_plural': 'Admission: Denied Students'},
        ),
        migrations.AlterModelOptions(
            name='distinguishedstudent',
            options={'verbose_name_plural': 'Admission: Distinguished Students'},
        ),
        migrations.AlterModelOptions(
            name='graduationyear',
            options={'ordering': ['-display_order'], 'verbose_name_plural': 'Admission: Graduation Years'},
        ),
        migrations.AlterModelOptions(
            name='importantdatesidebar',
            options={'ordering': ['display_order'], 'verbose_name_plural': 'Admission: Important Date Sidebar'},
        ),
        migrations.AlterModelOptions(
            name='kfupmidspool',
            options={'verbose_name_plural': 'Registrar: KFUPM ID Pools'},
        ),
        migrations.AlterModelOptions(
            name='lookup',
            options={'ordering': ['lookup_type', '-display_order'], 'verbose_name_plural': 'Admission: Look ups'},
        ),
        migrations.AlterModelOptions(
            name='nationality',
            options={'ordering': ['display_order', 'nationality_en'], 'verbose_name_plural': 'Admission: Nationalities'},
        ),
        migrations.AlterModelOptions(
            name='registrationstatus',
            options={'verbose_name_plural': 'Admission: Registration Status'},
        ),
        migrations.AlterModelOptions(
            name='registrationstatusmessage',
            options={'verbose_name_plural': 'Admission: Registration Status Messages'},
        ),
        migrations.RemoveField(
            model_name='user',
            name='admission_letter_note',
        ),
        migrations.AddField(
            model_name='user',
            name='english_level',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='English Level'),
        ),
        migrations.AddField(
            model_name='user',
            name='english_placement_test_score',
            field=models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)], verbose_name='English Placement Test Score'),
        ),
        migrations.AddField(
            model_name='user',
            name='english_speaking_test_score',
            field=models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)], verbose_name='English Speaking Test Score'),
        ),
        migrations.AlterField(
            model_name='user',
            name='high_school_gpa',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)], verbose_name='High School GPA'),
        ),
        migrations.AlterField(
            model_name='user',
            name='high_school_gpa_yesser',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)], verbose_name='High School GPA - Yesser'),
        ),
        migrations.AlterField(
            model_name='user',
            name='qudrat_score',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)], verbose_name='Qudrat Score'),
        ),
        migrations.AlterField(
            model_name='user',
            name='qudrat_score_yesser',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)], verbose_name='Qudrat Score - Yesser'),
        ),
        migrations.AlterField(
            model_name='user',
            name='tahsili_score',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)], verbose_name='Tahsili Score'),
        ),
        migrations.AlterField(
            model_name='user',
            name='tahsili_score_yesser',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)], verbose_name='Tahsili Score - Yesser'),
        ),
        migrations.AlterField(
            model_name='user',
            name='tarifi_week_attendance_date',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='undergraduate_admission.TarifiReceptionDate', verbose_name='Tarifi Week Attendance Date'),
        ),
        migrations.AddField(
            model_name='tarifireceptiondate',
            name='semester',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tarifi_reception_dates', to='undergraduate_admission.AdmissionSemester', verbose_name='Semester'),
        ),
    ]
