from django.db import models

from django.contrib.auth.models import User

class Student(User):
    # government_id = models.PositiveIntegerField()
    # emaill_address = models.EmailField()
    semester_id = models.ForeignKey(
        'AdmissionSemester',
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        related_name = 'applicants'
    )
    status_message_id = models.ForeignKey(
        'RegistrationStatusMessage',
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
    )
    admission_note = models.CharField(max_length=500)
    # first_name = models.CharField(max_length=50)
    # last_name = models.CharField(max_length=50)
    hs_full_name = models.CharField(max_length=500)
    qiyas_first_name = models.CharField(max_length=50)
    qiyas_second_name = models.CharField(max_length=50)
    qiyas_third_name = models.CharField(max_length=50)
    qiyas_last_name = models.CharField(max_length=50)
    first_name_en = models.CharField(max_length=50)
    second_name_en = models.CharField(max_length=50)
    third_name_en = models.CharField(max_length=50)
    last_name_en = models.CharField(max_length=50)
    nationality_id = models.ForeignKey(
        'Nationality',
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        limit_choices_to={'show_flag':True},
    )
    saudi_mother = models.NullBooleanField()
    birthday = models.DateField(null=True)
    birthday_ah = models.CharField(max_length=50)
    hs_graduation_year_id = models.ForeignKey(
        'GraduationYear',
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
    )
    mobile = models.CharField(max_length=50)
    guardian_mobile = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    kfupm_id = models.PositiveIntegerField(unique=True, null=True)
    updated_on = models.DateTimeField(auto_now=True, null=True)
    updated_by = models.ForeignKey(
        User,
        related_name='modified_students',
        null=True,
    )

    def get_actual_student_status(self):
        return "to be implemented"

    def __init__(self, *args, **kwargs):
        super(Student,self).__init__(*args, **kwargs)
        self._meta.get_field('username').verbose_name = 'Government ID'
        self._meta.get_field('email').verbose_name = 'Email Address'

    class Meta:
        verbose_name = "student"
        verbose_name_plural = "students"



class AdmissionSemester(models.Model):
    semester_name = models.CharField(max_length=200)
    phase1_start_date = models.DateTimeField(null=True)
    phase1_end_date = models.DateTimeField(null=True)
    phase2_start_date = models.DateTimeField(null=True)
    phase2_end_date = models.DateTimeField(null=True)

    def __str__(self):
        return self.semester_name

class RegistrationStatus(models.Model):
    status_ar = models.CharField(max_length=50)
    status_en = models.CharField(max_length=50)

    def __str__(self):
        return self.status_ar

class RegistrationStatusMessage(models.Model):
    status_message_ar = models.CharField(max_length=500)
    status_message_en = models.CharField(max_length=500)
    status_id = models.ForeignKey(
        'RegistrationStatus',
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
    )

    def __str__(self):
        return self.status_id.status_ar + " " + self.status_message_ar

class City(models.Model):
    city_name_ar = models.CharField(max_length=100)
    city_name_en = models.CharField(max_length=100)
    show_flag = models.BooleanField()
    display_order = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.city_name_ar

    class Meta:
        ordering=['-display_order']
        verbose_name_plural='cities'

class DeniedStudent(models.Model):
	government_id = models.CharField(max_length=12)
	student_name = models.CharField(max_length=400)
	message = models.CharField(max_length=400)
	university_code = models.CharField(max_length=10)
	semester_id = models.ForeignKey(
        'AdmissionSemester',
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
    )
	trial_date = models.DateTimeField()


class GraduationYear(models.Model):
    graduation_year_en = models.CharField(max_length=50)
    graduation_year_ar = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    show_flag = models.BooleanField()
    display_order = models.PositiveSmallIntegerField()

    class Meta:
        ordering=['-display_order']

class Nationality(models.Model):
    nationality_ar = models.CharField(max_length=50)
    nationality_en = models.CharField(max_length=50)
    show_flag = models.BooleanField()
    display_order = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.nationality_ar

    class Meta:
        ordering=['-display_order']
        verbose_name_plural = 'nationalities'

class Agreement(models.Model):
    semester_id = models.ForeignKey(
        'AdmissionSemester',
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
    )
    agreement_type = models.CharField(max_length=100)
    agreement_text_ar = models.CharField(max_length=2000)
    agreement_text_en = models.CharField(max_length=2000)
    show_flag = models.BooleanField()
    display_order = models.PositiveSmallIntegerField()
    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, related_name='agreements_modified')

    def __str__(self):
        return self.agreement_text_en

    class Meta:
        ordering=['-display_order']
