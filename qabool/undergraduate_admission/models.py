import datetime

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils import translation
from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):
    semester = models.ForeignKey(
        'AdmissionSemester',
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        related_name = 'applicants',
        verbose_name=_('Admission Semester'),
    )
    status_message = models.ForeignKey(
        'RegistrationStatusMessage',
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        verbose_name=_('Message Status'),
    )

    admission_note = models.CharField(null=True, blank=True, max_length=500, verbose_name=_('Admission Note'))

    nationality = models.ForeignKey(
        'Nationality',
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        limit_choices_to={'show': True},
        verbose_name=_('Nationality'),
    )
    saudi_mother = models.NullBooleanField(verbose_name=_('Saudi Mother'))
    birthday = models.DateField(null=True, verbose_name=_('Birthday'))

    birthday_ah = models.CharField(null=True, max_length=50, verbose_name=_('Birthday Hijri'))
    high_school_graduation_year = models.ForeignKey(
        'GraduationYear',
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        verbose_name=_('Graduation Year'),
    )
    mobile = models.CharField(
        null=True,
        blank=False,
        max_length=50,
        verbose_name=_('Mobile'),
        help_text=_('Mobile number should be of this format "966xxxxxxxxx" '),
        validators=[
            RegexValidator(
                '^966\d{9}$',
                message=_('You have entered an invalid mobile number')
            ),
        ]
    )
    phone = models.CharField(null=True, max_length=50, verbose_name=_('Phone'))
    high_school_gpa = models.FloatField(null=True, blank=True, verbose_name=_('High School GPA'))
    qudrat_score = models.FloatField(null=True, blank=True, verbose_name=_('Qudrat Score'))
    tahsili_score = models.FloatField(null=True, blank=True, verbose_name=_('Tahsili Score'))
    kfupm_id = models.PositiveIntegerField(unique=True, null=True, verbose_name=_('KFUPM ID'))
    first_name_ar = models.CharField(null=True,blank=True,max_length=50, verbose_name=_('First Name (Arabic)'))
    second_name_ar = models.CharField(null=True,blank=True,max_length=50, verbose_name=_('Second Name (Arabic)'))
    third_name_ar = models.CharField(null=True,blank=True,max_length=50, verbose_name=_('Third Name (Arabic)'))
    family_name_ar = models.CharField(null=True,blank=True,max_length=50, verbose_name=_('Family Name (Arabic)'))
    first_name_en = models.CharField(null=True,blank=True,max_length=50, verbose_name=_('First Name (English)'))
    second_name_en = models.CharField(null=True,blank=True,max_length=50, verbose_name=_('Second Name (English)'))
    third_name_en = models.CharField(null=True,blank=True,max_length=50, verbose_name=_('Third Name (English)'))
    family_name_en = models.CharField(null=True,blank=True,max_length=50, verbose_name=_('Family Name (English)'))
    mother_gov_id_file = models.CharField(null=True,blank=True,max_length=100, verbose_name=_('Mother Government ID'))
    birth_certificate = models.CharField(null=True,blank=True,max_length=100, verbose_name=_('Birth Date Certificate'))
    government_id_file = models.CharField(null=True,blank=True,max_length=100, verbose_name=_('Government ID File'))
    government_id_issue = models.DateTimeField(null=True,blank=True, verbose_name=_('Government ID Issue Date'))
    government_id_expiry = models.DateTimeField(null=True,blank=True, verbose_name=_('Government ID Expiry Date'))
    government_id_place = models.CharField(null=True,blank=True,max_length=50, verbose_name=_('Place of Issue'))
    passport_number = models.CharField(null=True,blank=True,max_length=50, verbose_name=_('Password Number'))
    passport_place = models.CharField(null=True,blank=True,max_length=50, verbose_name=_('Passport Place of Issue '))
    passport_expiry = models.DateTimeField(null=True,blank=True, verbose_name=_('Passport Expiry Date'))
    passport_file = models.CharField(null=True,blank=True,max_length=100,verbose_name=_('Upload Passport'))
    high_school_name = models.CharField(null=True,blank=True,max_length=100, verbose_name=_('High School Name'))
    high_school_system = models.CharField(null=True,blank=True,max_length=100, verbose_name=_('High School System'))
    high_school_province = models.CharField(null=True,blank=True,max_length=100, verbose_name=_('High School Province'))
    high_school_city = models.CharField(null=True,blank=True,max_length=100, verbose_name=_('High School City'))
    high_school_certificate = models.CharField(null=True,blank=True,max_length=100, verbose_name=_('High School Certificate'))
    courses_certificate = models.CharField(null=True,blank=True,max_length=100, verbose_name=_('Courses Certificate'))
    student_notes = models.CharField(null=True,blank=True,max_length=500, verbose_name=_('Student Notes'))
    personal_picture = models.CharField(null=True,blank=True,max_length=100, verbose_name=_('Personal Picture'))
    guardian_name = models.CharField(null=True,blank=True,max_length=50, verbose_name=_('Guardian Name'))
    guardian_government_id = models.CharField(null=True,blank=True,max_length=50, verbose_name=_('Guardian Government ID'))
    guardian_relation = models.CharField(null=True,blank=True,max_length=50, verbose_name=_('Guardian Relation'))
    guardian_phone = models.CharField(null=True,blank=True,max_length=50, verbose_name=_('Guardian Phone'))
    guardian_mobile = models.CharField(
        null=True,
        blank=True,
        max_length=50,
        verbose_name=_('Guardian Mobile'),
        help_text=_('Guardian mobile should be different than own mobile'),
        validators=[
            RegexValidator(
                '^9665\d{8}$',
                message=_('You have entered an invalid mobile number')
            ),
        ]
    )
    guardian_email = models.CharField(null=True,blank=True,max_length=50, verbose_name=_('Guardian Email'))
    guardian_po_box = models.CharField(null=True,blank=True,max_length=50, verbose_name=_('Guardian PO Box'))
    guardian_postal_code = models.CharField(null=True,blank=True,max_length=50, verbose_name=_('Guardian Postal Code'))
    guardian_city = models.CharField(null=True,blank=True,max_length=50, verbose_name=_('Guardian City'))
    guardian_job = models.CharField(null=True,blank=True,max_length=50, verbose_name=_('Guardian Work'))
    guardian_employer = models.CharField(null=True,blank=True,max_length=50, verbose_name=_('Guardian Employer'))
    blood_type = models.CharField(null=True,blank=True,max_length=50, verbose_name=_('Blood Type'))
    student_address = models.CharField(null=True,blank=True,max_length=500, verbose_name=_('Student Address'))
    social_status = models.CharField(null=True,blank=True,max_length=50, verbose_name=_('Social Status'))
    kids_no = models.CharField(null=True,blank=True,max_length=50, verbose_name=_('Number of Kids'))
    employment = models.CharField(null=True,blank=True,max_length=50, verbose_name=_('Employeement'))
    employer_name = models.CharField(null=True,blank=True,max_length=50, verbose_name=_('Employeer Name'))
    disability_needs = models.CharField(null=True,blank=True,max_length=50, verbose_name=_('Disability Type'))
    other_needs = models.CharField(null=True,blank=True,max_length=50, verbose_name=_('Other Disability'))
    chronic_diseases = models.CharField(null=True, blank=True, max_length=500, verbose_name=_('Chronic Diseases'))
    relative_name = models.CharField(null=True,blank=True,max_length=50, verbose_name=_('Relative Name'))
    relative_relation = models.CharField(null=True,blank=True,max_length=50, verbose_name=_('Relative Relation'))
    relative_phone = models.CharField(null=True,blank=True,max_length=50, verbose_name=_('Relative Mobile'))
    relative_po_box = models.CharField(null=True,blank=True,max_length=50, verbose_name=_('Relative PO Box'))
    relative_po_stal_code = models.CharField(null=True,blank=True,max_length=50, verbose_name=_('Relative PO Box'))
    relative_city = models.CharField(null=True,blank=True,max_length=50, verbose_name=_('Relative City'))
    relative_job = models.CharField(null=True,blank=True,max_length=50, verbose_name=_('Relative Work'))
    relative_employer = models.CharField(null=True,blank=True,max_length=50, verbose_name=_('Relative Employer'))
    admission_letter_print_date = models.DateTimeField(null=True,blank=True, verbose_name=_('Admission Letter Print Date'))
    admission_letter_note = models.CharField(null=True,blank=True,max_length=500, verbose_name=_('Admission Letter Note'))
    medical_report_print_date = models.DateTimeField(null=True,blank=True, verbose_name=_('Medical Report Print Date'))
    withdrawal_date = models.DateTimeField(null=True,blank=True, verbose_name=_('Withdrawal Date'))
    withdrawal_university = models.CharField(null=True,blank=True,max_length=100, verbose_name=_('Withdrew To University'))
    withdrawal_reason = models.CharField(null=True,blank=True,max_length=500, verbose_name=_('Withdrawal Reason'))
    phase2_start_date = models.DateTimeField(null=True,blank=True, verbose_name=_('Phase 2 Start Date'))
    phase2_end_date = models.DateTimeField(null=True,blank=True, verbose_name=_('Phase 2 End Date'))
    phase2_submit_date  = models.DateTimeField(null=True,blank=True, verbose_name=_('Phase 2 Submit Date'))
    verification_status = models.CharField(null=True,blank=True,max_length=500, verbose_name=_('Verification Status'))
    verification_notes = models.CharField(null=True,blank=True,max_length=500, verbose_name=_('Verification Note'))

    def get_actual_student_status(self):
        return self.status_message

    def __init__(self, *args, **kwargs):
        super(User,self).__init__(*args, **kwargs)
        self._meta.get_field('username').verbose_name = _('Government ID')

    def __str__(self):
        return self.first_name + ' ' + self.last_name # + ' (' + self.username + ')'

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"


class AdmissionSemester(models.Model):
    semester_name = models.CharField(max_length=200, verbose_name=_('Semester Name'))
    phase1_start_date = models.DateTimeField(null=True, verbose_name=_('Phase 1 Start Date'))
    phase1_end_date = models.DateTimeField(null=True, verbose_name=_('Phase 1 End Date'))
    phase2_start_date = models.DateTimeField(null=True, verbose_name=_('Phase 2 Start Date'))
    phase2_end_date = models.DateTimeField(null=True, verbose_name=_('Phase 2 End Date'))
    # results_date = models.DateTimeField(null=True, blank=False, verbose_name=_('Results Announcement Date'))
    high_school_gpa_weight = models.FloatField(null=True, blank=False, verbose_name=_('High School GPA Weight'))
    qudrat_score_weight = models.FloatField(null=True, blank=False, verbose_name=_('Qudrat Score Weight'))
    tahsili_score_weight = models.FloatField(null=True, blank=False, verbose_name=_('Tahsili Score Weight'))

    def __str__(self):
        return self.semester_name

    @staticmethod
    def get_phase1_active_semester():
        now = datetime.datetime.now()
        sem = AdmissionSemester.objects.filter(phase1_start_date__lte=now, phase1_end_date__gte=now).first()
        return sem


class RegistrationStatus(models.Model):
    status_ar = models.CharField(max_length=50, verbose_name=_('Status (Arabic)'))
    status_en = models.CharField(max_length=50, verbose_name=_('Status (English)'))
    status_code = models.CharField(max_length=20, null=True, blank=False)

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
    status_message_ar = models.CharField(max_length=500, verbose_name=_('Registration Status Message AR'))
    status_message_en = models.CharField(max_length=500, verbose_name=_('Registration Status Message EN'))
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


class Lookup(models.Model):
    lookup_type = models.CharField(max_length=20, null=True, blank=False)
    lookup_value_ar = models.CharField(max_length=100, null=True, blank=False)
    lookup_value_en = models.CharField(max_length=100, null=True, blank=False)
    show = models.BooleanField(verbose_name=_('Show'), default=True)
    display_order = models.PositiveSmallIntegerField(null=True, verbose_name=_('Display Order'))

    @property
    def lookup_value(self):
        lang = translation.get_language()
        if lang == "ar":
            return self.lookup_value_ar
        else:
            return self.lookup_value_en

    def __str__(self):
        return self.lookup_value

    class Meta:
        ordering=['-display_order']


class City(models.Model):
    city_name_ar = models.CharField(max_length=100, verbose_name=_('City Name Arabic'))
    city_name_en = models.CharField(max_length=100, verbose_name=_('City Name English'))
    show = models.BooleanField(verbose_name=_('Show'), default=True)
    display_order = models.PositiveSmallIntegerField(null=True, verbose_name=_('Display Order'))

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
    government_id = models.CharField(max_length=12, verbose_name=_('Government ID'))
    student_name = models.CharField(max_length=400, verbose_name=_('Student Name'))
    message = models.CharField(max_length=400, verbose_name=_('Message'))
    university_code = models.CharField(max_length=10, verbose_name=_('University Code'))
    semester = models.ForeignKey(
        'AdmissionSemester',
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        related_name='denied_students'
    )
    last_trial_date = models.DateTimeField(null=True, blank=True, verbose_name=_('Last Trial Date'))
    trials_count = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=_('Count Trial'))

    def __str__(self):
        return self.student_name + ' (' + self.government_id + ')'

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


class DistinguishedStudent(models.Model):
    government_id = models.CharField(max_length=12, verbose_name=_('Government ID'))
    student_name = models.CharField(max_length=400, verbose_name=_('Student Name'))
    city = models.CharField(max_length=400, verbose_name=_('City'))
    attended = models.BooleanField(verbose_name=_('Attended'), default=True)

    def __str__(self):
        return self.student_name + ' (' + self.government_id + ')'


class GraduationYear(models.Model):
    graduation_year_en = models.CharField(max_length=50, verbose_name=_('Graduation Year (English)'))
    graduation_year_ar = models.CharField(max_length=50, verbose_name=_('Graduation Year (Arabic)'))
    description = models.CharField(max_length=200, verbose_name=_('Description'))
    show = models.BooleanField(verbose_name=_('Show'), default=True)
    display_order = models.PositiveSmallIntegerField(null=True, verbose_name=_('Display Order'))

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
    nationality_ar = models.CharField(max_length=50, verbose_name=_('Nationality (Arabic)'))
    nationality_en = models.CharField(max_length=50, verbose_name=_('Nationality (English)'))
    show = models.BooleanField(verbose_name=_('Show'), default=True)
    display_order = models.PositiveSmallIntegerField(null=True, verbose_name=_('Display Order'))

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
        related_name='agreement',
        verbose_name= 'Semester',
    )
    agreement_type = models.CharField(max_length=100, null=True, blank=False, verbose_name=_('Agreement Type'))
    agreement_header_ar = models.TextField(max_length=2000, null=True, blank=True, verbose_name=_('Agreement Header (Arabic)'))
    agreement_header_en = models.TextField(max_length=2000, null=True, blank=True, verbose_name=_('Agreement Header (English)'))
    agreement_footer_ar = models.TextField(max_length=2000, null=True, blank=True, verbose_name=_('Agreement Footer (Arabic)'))
    agreement_footer_en = models.TextField(max_length=2000, null=True, blank=True, verbose_name=_('Agreement Footer (English)'))

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
        return self.agreement_type


class AgreementItem(models.Model):
    agreement = models.ForeignKey(
        'Agreement',
        on_delete=models.CASCADE,
        blank=False,
        null=True,
        related_name = 'items',
    )
    agreement_text_ar = models.CharField(max_length=2000, verbose_name=_('Agreement Text (Arabic)') )
    agreement_text_en = models.CharField(max_length=2000, verbose_name=_('Agreement Text (English)'))
    show = models.BooleanField(verbose_name=_('Show'), default=True)
    display_order = models.PositiveSmallIntegerField(null=True, verbose_name=_('Display Order'))

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
