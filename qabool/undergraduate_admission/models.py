import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import translation

class User(AbstractUser):
    semester = models.ForeignKey(
        'AdmissionSemester',
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        related_name = 'applicants'
    )
    status_message = models.ForeignKey(
        'RegistrationStatusMessage',
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
    )
    admission_note = models.CharField(null=True, blank=True, max_length=500)
    high_school_full_name = models.CharField(null=True, max_length=500)
    qiyas_first_name = models.CharField(null=True, max_length=50)
    qiyas_second_name = models.CharField(null=True, max_length=50)
    qiyas_third_name = models.CharField(null=True, max_length=50)
    qiyas_last_name = models.CharField(null=True, max_length=50)
    first_name_en = models.CharField(null=True, max_length=50)
    second_name_en = models.CharField(null=True, max_length=50)
    third_name_en = models.CharField(null=True, max_length=50)
    last_name_en = models.CharField(null=True, max_length=50)
    nationality = models.ForeignKey(
        'Nationality',
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        limit_choices_to={'show_flag':True},
    )
    saudi_mother = models.NullBooleanField()
    birthday = models.DateField(null=True)
    birthday_ah = models.CharField(null=True, max_length=50)
    high_school_graduation_year = models.ForeignKey(
        'GraduationYear',
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
    )
    mobile = models.CharField(null=True, blank=False, max_length=50)
    guardian_mobile = models.CharField(null=True, blank=False, max_length=50)
    phone = models.CharField(null=True, max_length=50)
    high_school_gpa = models.FloatField(null=True, blank=True)
    qudrat_score = models.FloatField(null=True, blank=True)
    tahsili_score = models.FloatField(null=True, blank=True)
    kfupm_id = models.PositiveIntegerField(unique=True, null=True)
    updated_on = models.DateTimeField(auto_now=True, null=True)
    updated_by = models.ForeignKey(
        'self',
        related_name='modified_students',
        null=True,
    )

    def get_actual_student_status(self):
        return self.status_message

    def __init__(self, *args, **kwargs):
        super(User,self).__init__(*args, **kwargs)
        self._meta.get_field('username').verbose_name = 'Government ID'

    def __str__(self):
        return self.first_name + ' ' + self.last_name #+ ' (' + self.username + ')'

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"


class AdmissionSemester(models.Model):
    semester_name = models.CharField(max_length=200)
    phase1_start_date = models.DateTimeField(null=True)
    phase1_end_date = models.DateTimeField(null=True)
    phase2_start_date = models.DateTimeField(null=True)
    phase2_end_date = models.DateTimeField(null=True)
    high_school_gpa_weight = models.FloatField(null=True, blank=False)
    qudrat_score_weight = models.FloatField(null=True, blank=False)
    tahsili_score_weight = models.FloatField(null=True, blank=False)

    def __str__(self):
        return self.semester_name

    @staticmethod
    def get_phase1_active_semester():
        now = datetime.datetime.now()
        sem = AdmissionSemester.objects.filter(phase1_start_date__lte=now, phase1_end_date__gte=now).first()
        return sem


class RegistrationStatus(models.Model):
    status_ar = models.CharField(max_length=50)
    status_en = models.CharField(max_length=50)

    @property
    def registration_status(self):
        lang = translation.get_language()
        if lang == "ar":
            return self.status_ar
        else:
            return self.status_en

    def __str__(self):
        return self.registration_status


class RegistrationStatusMessage(models.Model):
    status_message_ar = models.CharField(max_length=500)
    status_message_en = models.CharField(max_length=500)
    status = models.ForeignKey(
        'RegistrationStatus',
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
    )

    @property
    def registration_status_message(self):
        lang = translation.get_language()
        if lang == "ar":
            return self.status_message_ar
        else:
            return self.status_message_en

    def __str__(self):
        return self.status.registration_status + ". " + self.registration_status_message


class City(models.Model):
    city_name_ar = models.CharField(max_length=100)
    city_name_en = models.CharField(max_length=100)
    show_flag = models.BooleanField()
    display_order = models.PositiveSmallIntegerField(null=True)

    @property
    def city(self):
        lang = translation.get_language()
        if lang == "ar":
            return self.city_name_ar
        else:
            return self.city_name_en

    def __str__(self):
        return self.city

    class Meta:
        ordering=['-display_order']
        verbose_name_plural='cities'


class DeniedStudent(models.Model):
    government_id = models.CharField(max_length=12)
    student_name = models.CharField(max_length=400)
    message = models.CharField(max_length=400)
    university_code = models.CharField(max_length=10)
    semester = models.ForeignKey(
        'AdmissionSemester',
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        related_name='denied_students'
    )
    last_trial_date = models.DateTimeField(null=True, blank=True)
    trials_count = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self):
        return self.student_name + ' ' + self.government_id

    @staticmethod
    def check_if_student_is_denied(govid):
        activeSem = AdmissionSemester.get_phase1_active_semester()
        denied = activeSem.denied_students.filter(government_id = govid).first()

        if denied:
            denied.last_trial_date = datetime.datetime.now()
            if denied.trials_count is None:
                denied.trials_count = 0
            denied.trials_count += 1
            denied.save()

            return denied.message


class GraduationYear(models.Model):
    graduation_year_en = models.CharField(max_length=50)
    graduation_year_ar = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    show_flag = models.BooleanField()
    display_order = models.PositiveSmallIntegerField(null=True)

    class Meta:
        ordering=['-display_order']

    @property
    def graduation_year(self):
        lang = translation.get_language()
        if lang == "ar":
            return self.graduation_year_ar
        else:
            return self.graduation_year_en

    def __str__(self):
        return self.graduation_year


class Nationality(models.Model):
    nationality_ar = models.CharField(max_length=50)
    nationality_en = models.CharField(max_length=50)
    show_flag = models.BooleanField()
    display_order = models.PositiveSmallIntegerField(null=True)

    @property
    def nationality(self):
        lang = translation.get_language()
        if lang == "ar":
            return self.nationality_ar
        else:
            return self.nationality_en

    def __str__(self):
        return self.nationality

    class Meta:
        ordering=['display_order', 'nationality_en']
        verbose_name_plural = 'nationalities'


class Agreement(models.Model):
    semester = models.ForeignKey(
        'AdmissionSemester',
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
    )
    agreement_type = models.CharField(max_length=100, null=True, blank=False)
    agreement_header_ar = models.TextField(max_length=2000, null=True, blank=True)
    agreement_header_en = models.TextField(max_length=2000, null=True, blank=True)
    agreement_footer_ar = models.TextField(max_length=2000, null=True, blank=True)
    agreement_footer_en = models.TextField(max_length=2000, null=True, blank=True)

    @property
    def agreement_header(self):
        lang = translation.get_language()
        if lang == "ar":
            return self.agreement_header_ar
        else:
            return self.agreement_header_en

    @property
    def agreement_footer(self):
        lang = translation.get_language()
        if lang == "ar":
            return self.agreement_footer_ar
        else:
            return self.agreement_footer_en

    def __str__(self):
        return self.agreement_header


class AgreementItem(models.Model):
    agreement = models.ForeignKey(
        'Agreement',
        on_delete=models.CASCADE,
        blank=False,
        null=True,
        related_name = 'items',
    )
    agreement_text_ar = models.CharField(max_length=2000)
    agreement_text_en = models.CharField(max_length=2000)
    show_flag = models.BooleanField()
    display_order = models.PositiveSmallIntegerField(null=True)
    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, related_name='agreements_modified', null=True, blank=True)

    @property
    def agreement_item(self):
        lang = translation.get_language()
        if lang == "ar":
            return self.agreement_text_ar
        else:
            return self.agreement_text_en

    def __str__(self):
        return self.agreement_item

    class Meta:
        ordering=['agreement', '-display_order']
