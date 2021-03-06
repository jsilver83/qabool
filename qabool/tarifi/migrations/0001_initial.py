# Generated by Django 2.1.5 on 2019-07-31 13:27

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('undergraduate_admission', '0008_auto_20190711_1554'),
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
                ('attender', models.ForeignKey(blank=True, limit_choices_to={'is_staff': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_slots', to=settings.AUTH_USER_MODEL, verbose_name='Attender')),
                ('semester', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tarifi_activities_dates', to='undergraduate_admission.AdmissionSemester', verbose_name='Semester')),
            ],
            options={
                'ordering': ['display_order', 'slot_start_date'],
                'verbose_name_plural': 'Tarifi: Preparation Activity Slots',
            },
        ),
        migrations.CreateModel(
            name='TarifiData',
            fields=[
                ('admission_request', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='tarifi_data', serialize=False, to='undergraduate_admission.AdmissionRequest')),
                ('preparation_course_attendance', models.DateTimeField(blank=True, null=True, verbose_name='Preparation Course Attendance Date')),
                ('english_speaking_test_start_time', models.DateTimeField(blank=True, null=True, verbose_name='English Speaking Test Time')),
                ('english_placement_test_score', models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)], verbose_name='English Placement Test Score')),
                ('english_speaking_test_score', models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)], verbose_name='English Speaking Test Score')),
                ('english_level', models.CharField(blank=True, max_length=20, null=True, verbose_name='English Level')),
                ('creation_date', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Reception Date')),
                ('updated_on', models.DateTimeField(auto_now=True, null=True, verbose_name='Updated On')),
                ('english_placement_test_slot', models.ForeignKey(blank=True, limit_choices_to={'type': 'ENGLISH_PLACEMENT_TEST'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='students_in_placement_slot', to='tarifi.TarifiActivitySlot', verbose_name='English Placement Test Slot')),
                ('english_speaking_test_slot', models.ForeignKey(blank=True, limit_choices_to={'type': 'ENGLISH_SPEAKING_TEST'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='students_in_speaking_slot', to='tarifi.TarifiActivitySlot', verbose_name='English Speaking Test Slot')),
                ('preparation_course_attended_by', models.ForeignKey(blank=True, limit_choices_to={'is_staff': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='attended_students', to=settings.AUTH_USER_MODEL, verbose_name='Preparation Course Attended By')),
                ('preparation_course_slot', models.ForeignKey(blank=True, limit_choices_to={'type': 'PREPARATION_COURSE'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='students_in_course_slot', to='tarifi.TarifiActivitySlot', verbose_name='Preparation Course Slot')),
                ('received_by', models.ForeignKey(blank=True, limit_choices_to={'is_staff': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='students_received', to=settings.AUTH_USER_MODEL, verbose_name='Received By')),
            ],
        ),
    ]
