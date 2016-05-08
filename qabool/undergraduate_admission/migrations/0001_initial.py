# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-08 10:48
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.auth.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0007_alter_validators_add_error_messages'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=30, unique=True, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.')], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('admission_note', models.CharField(blank=True, max_length=500, null=True)),
                ('high_school_full_name', models.CharField(max_length=500, null=True)),
                ('qiyas_first_name', models.CharField(max_length=50, null=True)),
                ('qiyas_second_name', models.CharField(max_length=50, null=True)),
                ('qiyas_third_name', models.CharField(max_length=50, null=True)),
                ('qiyas_last_name', models.CharField(max_length=50, null=True)),
                ('first_name_en', models.CharField(max_length=50, null=True)),
                ('second_name_en', models.CharField(max_length=50, null=True)),
                ('third_name_en', models.CharField(max_length=50, null=True)),
                ('last_name_en', models.CharField(max_length=50, null=True)),
                ('saudi_mother', models.NullBooleanField()),
                ('birthday', models.DateField(null=True)),
                ('birthday_ah', models.CharField(max_length=50, null=True)),
                ('mobile', models.CharField(max_length=50, null=True)),
                ('guardian_mobile', models.CharField(max_length=50, null=True)),
                ('phone', models.CharField(max_length=50, null=True)),
                ('high_school_gpa', models.FloatField(blank=True, null=True)),
                ('qudrat_score', models.FloatField(blank=True, null=True)),
                ('tahsili_score', models.FloatField(blank=True, null=True)),
                ('kfupm_id', models.PositiveIntegerField(null=True, unique=True)),
                ('updated_on', models.DateTimeField(auto_now=True, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='AdmissionSemester',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semester_name', models.CharField(max_length=200)),
                ('phase1_start_date', models.DateTimeField(null=True)),
                ('phase1_end_date', models.DateTimeField(null=True)),
                ('phase2_start_date', models.DateTimeField(null=True)),
                ('phase2_end_date', models.DateTimeField(null=True)),
                ('high_school_gpa_weight', models.FloatField(null=True)),
                ('qudrat_score_weight', models.FloatField(null=True)),
                ('tahsili_score_weight', models.FloatField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Agreement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('agreement_type', models.CharField(max_length=100, null=True)),
                ('agreement_header_ar', models.TextField(blank=True, max_length=2000, null=True)),
                ('agreement_header_en', models.TextField(blank=True, max_length=2000, null=True)),
                ('agreement_footer_ar', models.TextField(blank=True, max_length=2000, null=True)),
                ('agreement_footer_en', models.TextField(blank=True, max_length=2000, null=True)),
                ('semester', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='undergraduate_admission.AdmissionSemester')),
            ],
        ),
        migrations.CreateModel(
            name='AgreementItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('agreement_text_ar', models.CharField(max_length=2000)),
                ('agreement_text_en', models.CharField(max_length=2000)),
                ('show_flag', models.BooleanField()),
                ('display_order', models.PositiveSmallIntegerField()),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('semester', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='undergraduate_admission.Agreement')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agreements_modified', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['semester', '-display_order'],
            },
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city_name_ar', models.CharField(max_length=100)),
                ('city_name_en', models.CharField(max_length=100)),
                ('show_flag', models.BooleanField()),
                ('display_order', models.PositiveSmallIntegerField()),
            ],
            options={
                'verbose_name_plural': 'cities',
                'ordering': ['-display_order'],
            },
        ),
        migrations.CreateModel(
            name='DeniedStudent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('government_id', models.CharField(max_length=12)),
                ('student_name', models.CharField(max_length=400)),
                ('message', models.CharField(max_length=400)),
                ('university_code', models.CharField(max_length=10)),
                ('last_trial_date', models.DateTimeField(blank=True, null=True)),
                ('trials_count', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('semester', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='denied_students', to='undergraduate_admission.AdmissionSemester')),
            ],
        ),
        migrations.CreateModel(
            name='GraduationYear',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('graduation_year_en', models.CharField(max_length=50)),
                ('graduation_year_ar', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=200)),
                ('show_flag', models.BooleanField()),
                ('display_order', models.PositiveSmallIntegerField()),
            ],
            options={
                'ordering': ['-display_order'],
            },
        ),
        migrations.CreateModel(
            name='Nationality',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nationality_ar', models.CharField(max_length=50)),
                ('nationality_en', models.CharField(max_length=50)),
                ('show_flag', models.BooleanField()),
                ('display_order', models.PositiveSmallIntegerField()),
            ],
            options={
                'verbose_name_plural': 'nationalities',
                'ordering': ['-display_order'],
            },
        ),
        migrations.CreateModel(
            name='RegistrationStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status_ar', models.CharField(max_length=50)),
                ('status_en', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='RegistrationStatusMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status_message_ar', models.CharField(max_length=500)),
                ('status_message_en', models.CharField(max_length=500)),
                ('status', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='undergraduate_admission.RegistrationStatus')),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='high_school_graduation_year',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='undergraduate_admission.GraduationYear'),
        ),
        migrations.AddField(
            model_name='user',
            name='nationality',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='undergraduate_admission.Nationality'),
        ),
        migrations.AddField(
            model_name='user',
            name='semester',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='applicants', to='undergraduate_admission.AdmissionSemester'),
        ),
        migrations.AddField(
            model_name='user',
            name='status_message',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='undergraduate_admission.RegistrationStatusMessage'),
        ),
        migrations.AddField(
            model_name='user',
            name='updated_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='modified_students', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]