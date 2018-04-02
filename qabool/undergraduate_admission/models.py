from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.db import OperationalError
from django.utils import timezone

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from undergraduate_admission.media_handlers import upload_location_govid, upload_location_birth, \
    upload_location_mother_govid, upload_location_passport, upload_location_certificate, \
    upload_location_picture, upload_location_courses, upload_location_withdrawal_proof, \
    upload_location_driving_license, upload_location_vehicle_registration
from undergraduate_admission.validators import validate_file_extension, validate_image_extension


# TODO: split user fields into two groups: essential and non essential fields
class User(AbstractUser):
    semester = models.ForeignKey(
        'AdmissionSemester',
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        related_name='applicants',
        verbose_name=_('Admission Semester'),
        db_index=True,
    )
    status_message = models.ForeignKey(
        'RegistrationStatusMessage',
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        verbose_name=_('Message Status'),
    )
    admission_note = models.CharField(null=True, blank=True, max_length=500, verbose_name=_('Admission Note'))
    admission_note2 = models.CharField(null=True, blank=True, max_length=500, verbose_name=_('Admission Note 2'))
    admission_note3 = models.CharField(null=True, blank=True, max_length=500, verbose_name=_('Admission Note 3'))
    nationality = models.ForeignKey(
        'Nationality',
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        limit_choices_to={'show': True},
        verbose_name=_('Nationality'),
    )
    saudi_mother = models.NullBooleanField(verbose_name=_('Saudi Mother'))
    saudi_mother_gov_id = models.CharField(verbose_name=_('Saudi Mother Government ID'), max_length=15, null=True,
                                           blank=True,
                                           validators=[
                                               RegexValidator(
                                                   '^\d{9,11}$',
                                                   message=_("You have entered an invalid Government ID")
                                               ), ])
    birthday = models.DateField(null=True, blank=True, verbose_name=_('Birthday'))
    birthday_ah = models.CharField(null=True, blank=True, max_length=50, verbose_name=_('Birthday Hijri'))
    birth_place = models.CharField(null=True,
                                   blank=True,
                                   max_length=100,
                                   verbose_name=_('Birth Place'),
                                   help_text=_('Country and city. e.g. Saudi Arabia Jeddah'))
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
        max_length=12,
        verbose_name=_('Mobile'),
        help_text=_(
            'Mobile number should be of this format "9665xxxxxxxx". Use English numerals only. Please make sure to activate promotional messages from your mobile provider.'),
        validators=[
            RegexValidator(
                '^(9665|٩٦٦٥)\d{8}$',
                message=_('You have entered an invalid mobile number')
            ),
        ],
        db_index=True,
    )
    high_school_gpa = models.FloatField(null=True, blank=True, verbose_name=_('High School GPA (Ministry)'),
                                        validators=[MinValueValidator(1), MaxValueValidator(100)],
                                        )
    phone = models.CharField(null=True,
                             blank=True,
                             max_length=50,
                             verbose_name=_('Phone'),
                             help_text=_('With country and area code. e.g. 966138602722'), )
    qudrat_score = models.FloatField(null=True, blank=True, verbose_name=_('Qudrat Score (Qiyas)'),
                                     validators=[MinValueValidator(1), MaxValueValidator(100)], )
    tahsili_score = models.FloatField(null=True, blank=True, verbose_name=_('Tahsili Score (Qiyas)'),
                                      validators=[MinValueValidator(1), MaxValueValidator(100)], )
    high_school_gpa_student_entry = models.FloatField(null=True, blank=True,
                                                      verbose_name=_('High School GPA'),
                                                      validators=[MinValueValidator(1), MaxValueValidator(100)], )
    qudrat_score_student_entry = models.FloatField(null=True, blank=True,
                                                   verbose_name=_('Qudrat Score - Entered by Student'),
                                                   validators=[MinValueValidator(1), MaxValueValidator(100)], )
    tahsili_score_student_entry = models.FloatField(null=True, blank=True,
                                                    verbose_name=_('Tahsili Score - Entered by Student'),
                                                    validators=[MinValueValidator(1), MaxValueValidator(100)], )
    kfupm_id = models.PositiveIntegerField(unique=True, null=True, blank=True, verbose_name=_('KFUPM ID'))
    first_name_ar = models.CharField(null=True, blank=True, max_length=50, verbose_name=_('First Name (Arabic)'))
    second_name_ar = models.CharField(null=True, blank=True, max_length=50, verbose_name=_('Second Name (Arabic)'))
    third_name_ar = models.CharField(null=True, blank=True, max_length=50, verbose_name=_('Third Name (Arabic)'))
    family_name_ar = models.CharField(null=True, blank=True, max_length=50, verbose_name=_('Family Name (Arabic)'))
    student_full_name_ar = models.CharField(null=True, blank=True, max_length=400,
                                            verbose_name=_('Student Full Name (Arabic)'),
                                            help_text=_(
                                                'Your Arabic full name should be similar to Identification ID/Iqama.'))
    first_name_en = models.CharField(null=True, blank=True, max_length=50, verbose_name=_('First Name (English)'))
    second_name_en = models.CharField(null=True, blank=True, max_length=50, verbose_name=_('Second Name (English)'))
    third_name_en = models.CharField(null=True, blank=True, max_length=50, verbose_name=_('Third Name (English)'))
    family_name_en = models.CharField(null=True, blank=True, max_length=50, verbose_name=_('Family Name (English)'))
    student_full_name_en = models.CharField(null=True, blank=True, max_length=400,
                                            verbose_name=_('Student Full Name (English)'),
                                            help_text=_('Your English full name should be similar to Passport '
                                                        'or high school certificate.'))

    GENDER_CHOICES = (
        ('M', _('Male')),
        ('F', _('Female'))
    )
    gender = models.CharField(choices=GENDER_CHOICES, max_length=128, default='M', verbose_name=_('Gender'))

    mother_gov_id_file = models.FileField(
        null=True,
        blank=True,
        max_length=100,
        verbose_name=_('Mother Government ID'),
        upload_to=upload_location_mother_govid,
        validators=[validate_file_extension],
    )
    birth_certificate = models.FileField(
        null=True,
        blank=True,
        max_length=100,
        verbose_name=_('Birth Date Certificate'),
        upload_to=upload_location_birth,
        validators=[validate_file_extension],
    )
    government_id_file = models.FileField(
        null=True,
        blank=True,
        max_length=100,
        verbose_name=_('Government ID File'),
        upload_to=upload_location_govid,
        validators=[validate_file_extension],
    )
    government_id_issue = models.DateTimeField(null=True, blank=True, verbose_name=_('Government ID Issue Date'))
    government_id_expiry = models.CharField(null=True, blank=True, max_length=20,
                                            verbose_name=_('Government ID Expiry Date'))
    government_id_place = models.CharField(null=True, blank=True, max_length=50,
                                           verbose_name=_('Government ID Place of Issue'))
    passport_number = models.CharField(null=True, blank=True, max_length=50, verbose_name=_('Passport Number'))
    passport_place = models.CharField(null=True, blank=True, max_length=50, verbose_name=_('Passport Place of Issue '))
    passport_expiry = models.DateTimeField(null=True, blank=True, verbose_name=_('Passport Expiry Date'))
    passport_file = models.FileField(
        null=True,
        blank=True,
        max_length=100,
        verbose_name=_('Upload Passport'),
        upload_to=upload_location_passport,
        validators=[validate_file_extension],
    )
    high_school_name = models.CharField(null=True, blank=True, max_length=100, verbose_name=_('High School Name'))
    high_school_system = models.CharField(null=True, blank=True, max_length=100, verbose_name=_('High School System'))
    high_school_major = models.CharField(null=True, blank=True, max_length=100, verbose_name=_('High School Major'))
    high_school_province = models.CharField(null=True, blank=True, max_length=100,
                                            verbose_name=_('High School Province'))
    high_school_city = models.CharField(null=True, blank=True, max_length=100, verbose_name=_('High School City'))
    high_school_certificate = models.FileField(
        null=True,
        blank=True,
        max_length=100,
        verbose_name=_('High School Certificate'),
        upload_to=upload_location_certificate,
        validators=[validate_file_extension],
    )
    courses_certificate = models.FileField(
        null=True,
        blank=True,
        max_length=100,
        verbose_name=_('Courses Certificate'),
        upload_to=upload_location_courses,
        validators=[validate_file_extension],
    )
    student_notes = models.TextField(null=True, blank=True, max_length=500, verbose_name=_('Student Notes'))
    personal_picture = models.FileField(
        null=True,
        blank=True,
        max_length=100,
        verbose_name=_('Personal Picture'),
        upload_to=upload_location_picture,
        validators=[validate_image_extension],
    )
    guardian_name = models.CharField(null=True, blank=True, max_length=50, verbose_name=_('Guardian Name'))
    guardian_government_id = models.CharField(null=True, blank=True, max_length=50,
                                              verbose_name=_('Guardian Government ID'))
    guardian_relation = models.CharField(null=True, blank=True, max_length=50, verbose_name=_('Guardian Relation'))
    guardian_phone = models.CharField(null=True,
                                      blank=True,
                                      max_length=50,
                                      verbose_name=_('Guardian Phone'),
                                      help_text=_('With country and area code. e.g. 966138602722'), )
    guardian_mobile = models.CharField(
        null=True,
        blank=True,
        max_length=12,
        verbose_name=_('Guardian Mobile'),
        help_text=_('Guardian mobile should be different than own mobile'),
        validators=[
            RegexValidator(
                '^(9665|٩٦٦٥)\d{8}$',
                message=_('You have entered an invalid mobile number')
            ),
        ]
    )
    guardian_email = models.EmailField(null=True, blank=True, max_length=50, verbose_name=_('Guardian Email'))
    guardian_po_box = models.CharField(null=True, blank=True, max_length=50, verbose_name=_('Guardian PO Box'))
    guardian_postal_code = models.CharField(null=True, blank=True, max_length=50,
                                            verbose_name=_('Guardian Postal Code'))
    guardian_city = models.CharField(null=True, blank=True, max_length=50, verbose_name=_('Guardian City'))
    guardian_job = models.CharField(null=True, blank=True, max_length=50, verbose_name=_('Guardian Work'))
    guardian_employer = models.CharField(null=True, blank=True, max_length=50, verbose_name=_('Guardian Employer'))
    blood_type = models.CharField(null=True, blank=True, max_length=50, verbose_name=_('Blood Type'))
    student_address = models.CharField(null=True, blank=True, max_length=500, verbose_name=_('Student Address'))
    social_status = models.CharField(null=True, blank=True, max_length=50, verbose_name=_('Social Status'))
    kids_no = models.CharField(null=True, blank=True, max_length=50, verbose_name=_('Number of Kids'))
    is_employed = models.BooleanField(
        verbose_name=_('Are You Employed?'),
        default=False,
        help_text=_('It is required that applicant be unemployed to be full-time. In case you are currently employed,'
                    ' you need to bring clearance from your employer.')
    )
    employer_name = models.CharField(null=True, blank=True, max_length=50, verbose_name=_('Employer Name'))
    is_disabled = models.BooleanField(
        verbose_name=_('Do you have any disabilities?'),
        default=False,
        help_text=_('This will let us help you better and will not affect your acceptance chances.'),
    )
    disability_needs = models.CharField(null=True, blank=True, max_length=50, verbose_name=_('Disability Type'))
    disability_needs_notes = models.TextField(null=True,
                                              blank=True,
                                              max_length=1000,
                                              verbose_name=_('Other Disability'))
    is_diseased = models.BooleanField(
        verbose_name=_('Do you have any chronic diseases?'),
        default=False,
        help_text=_('This will let us help you better and will not affect your acceptance chances.'),
    )
    chronic_diseases = models.CharField(null=True, blank=True, max_length=500, verbose_name=_('Chronic Diseases'))
    chronic_diseases_notes = models.TextField(null=True,
                                              blank=True,
                                              max_length=1000,
                                              verbose_name=_('Chronic Diseases Notes'))
    relative_name = models.CharField(null=True, blank=True, max_length=50, verbose_name=_('Relative Name'))
    relative_relation = models.CharField(null=True, blank=True, max_length=50, verbose_name=_('Relative Relation'))
    relative_phone = models.CharField(null=True,
                                      blank=True,
                                      max_length=50,
                                      verbose_name=_('Relative Mobile'),
                                      help_text=_('With country and area code. e.g. 966138602722'), )
    relative_po_box = models.CharField(null=True, blank=True, max_length=50, verbose_name=_('Relative PO Box'))
    relative_po_stal_code = models.CharField(null=True,
                                             blank=True,
                                             max_length=50,
                                             verbose_name=_('Relative Postal Code'))
    relative_city = models.CharField(null=True, blank=True, max_length=50, verbose_name=_('Relative City'))
    relative_job = models.CharField(null=True, blank=True, max_length=50, verbose_name=_('Relative Work'))
    relative_employer = models.CharField(null=True, blank=True, max_length=50, verbose_name=_('Relative Employer'))
    have_a_vehicle = models.BooleanField(
        verbose_name=_('Do you have a vehicle you want to register?'),
        default=False,
        help_text=_('This will let us help you better to get you a permit to enter campus.'),
    )
    vehicle_plate_no = models.CharField(null=True, blank=True, max_length=100,
                                        verbose_name=_('Vehicle Plate No.'))
    vehicle_registration_file = models.FileField(
        null=True,
        blank=True,
        max_length=100,
        verbose_name=_('Vehicle Registration File'),
        upload_to=upload_location_vehicle_registration,
        validators=[validate_file_extension],
    )
    driving_license_file = models.FileField(
        null=True,
        blank=True,
        max_length=100,
        verbose_name=_('Driving License File'),
        upload_to=upload_location_driving_license,
        validators=[validate_file_extension],
    )
    admission_letter_print_date = models.DateTimeField(null=True,
                                                       blank=True,
                                                       verbose_name=_('Admission Letter Print Date'))
    medical_report_print_date = models.DateTimeField(null=True,
                                                     blank=True,
                                                     verbose_name=_('Medical Report Print Date'))
    withdrawal_date = models.DateTimeField(null=True, blank=True, verbose_name=_('Withdrawal Date'))
    withdrawal_university = models.CharField(null=True,
                                             blank=True,
                                             max_length=100,
                                             verbose_name=_('Withdrew To University'))
    withdrawal_reason = models.CharField(null=True,
                                         blank=True,
                                         max_length=500,
                                         verbose_name=_('Withdrawal Reason'))
    phase2_start_date = models.DateTimeField(null=True, blank=True, verbose_name=_('Phase 2 Start Date'))
    phase2_end_date = models.DateTimeField(null=True, blank=True, verbose_name=_('Phase 2 End Date'))
    phase3_start_date = models.DateTimeField(null=True, blank=True, verbose_name=_('Phase 3 Start Date'))
    phase3_end_date = models.DateTimeField(null=True, blank=True, verbose_name=_('Phase 3 End Date'))
    phase2_submit_date = models.DateTimeField(null=True, blank=True, verbose_name=_('Phase 2 Submit Date'))
    phase3_submit_date = models.DateTimeField(null=True, blank=True, verbose_name=_('Phase 3 Submit Date'))

    verification_committee_member = models.CharField(null=True, blank=True, max_length=50,
                                                     verbose_name=_('Assigned Committee Member'))
    verification_documents_incomplete = models.NullBooleanField(blank=True,
                                                                verbose_name=_('Uploaded docs are incomplete?'), )
    # TODO: change field name to verification_picture_unacceptable
    verification_picture_acceptable = models.NullBooleanField(blank=True,
                                                              verbose_name=_('Uploaded picture is rejected?'), )
    verification_status = models.CharField(null=True, blank=True, max_length=500,
                                           verbose_name=_('Issues With Uploaded Docs'))
    verification_notes = models.CharField(null=True, blank=True, max_length=500, verbose_name=_('Verification Note'))
    withdrawal_proof_letter = models.FileField(
        null=True,
        blank=True,
        max_length=100,
        verbose_name=_('Withdrawal Proof Letter'),
        upload_to=upload_location_withdrawal_proof,
        validators=[validate_file_extension],
    )
    eligible_for_housing = models.NullBooleanField(verbose_name=_('Eligible For Housing'))
    roommate_id = models.CharField(max_length=20, null=True, blank=True, verbose_name=_('Roommate ID'))
    tarifi_week_attendance_date = models.ForeignKey('TarifiReceptionDate',
                                                    verbose_name=_('Tarifi Week Attendance Date'),
                                                    on_delete=models.SET_NULL,
                                                    null=True,
                                                    blank=True, )

    def get_verification_status(self):
        return self.verification_status

    get_verification_status.short_description = _('Issues With Uploaded Docs')

    def get_student_full_name(self):
        if self.first_name_ar and self.second_name_ar and self.family_name_ar:
            return '%s %s %s %s' % (self.first_name_ar, self.second_name_ar, self.third_name_ar, self.family_name_ar)
        elif self.student_full_name_ar:
            return '%s' % (self.student_full_name_ar, )
        elif self.is_staff:
            return self.username
        else:
            return 'ERROR: You do NOT have a name. Contact the admins about this ASAP'

    get_student_full_name.short_description = _('Full Name')

    def get_student_registration_status(self):
        try:
            return self.status_message.status
        except AttributeError:  # admins don't have status
            pass

    def get_actual_student_status(self):
        return self.status_message

    def get_student_phase(self):
        try:
            return self.status_message.status.status_code
        except:
            return 'REJECTED'

    @property
    def student_type(self):
        student_type = 'S'

        if self.nationality:
            if self.nationality.nationality_en != 'Saudi Arabia' and self.saudi_mother:
                student_type = 'M'
            elif self.nationality.nationality_en != 'Saudi Arabia':
                student_type = 'N'
        else:
            student_type = 'N/A'

        return student_type

    @property
    def admission_total(self):
        semester = self.semester
        if semester and self.high_school_gpa and self.qudrat_score and self.tahsili_score:
            return self.high_school_gpa * (semester.high_school_gpa_weight / 100) \
                   + self.qudrat_score * (semester.qudrat_score_weight / 100) \
                   + self.tahsili_score * (semester.tahsili_score_weight / 100)
        else:
            return 0.0

    # it will be used in setting status to EXPIRED auto
    @property
    def is_phase2_confirmation_expired(self):
        return False if AdmissionSemester.get_phase2_active_semester(self) else True

    @staticmethod
    def get_distinct_high_school_city(add_dashes=True):
        try:
            choices = User.objects.filter(eligible_for_housing=True, housing_user__searchable=True). \
                order_by().values('high_school_city').distinct()

            ch = [(o['high_school_city'], o['high_school_city']) for o in choices]
            if add_dashes:
                ch.insert(0, ('', '---------'))

            return ch
        except:  # was OperationalError and happened when db doesn't exist yet but later changed it to general except to catch an weird exceptions like ProgrammingError
            return [('--', '--')]

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self._meta.get_field('username').verbose_name = _('Government ID')

    def __str__(self):
        return self.get_student_full_name()

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"


# TODO: add a flag for active semester that will be used in mau places
class AdmissionSemester(models.Model):
    semester_name = models.CharField(max_length=200, verbose_name=_('Semester Name'))
    phase1_start_date = models.DateTimeField(null=True, verbose_name=_('Phase 1 Start Date'))
    phase1_end_date = models.DateTimeField(null=True, verbose_name=_('Phase 1 End Date'))
    phase2_start_date = models.DateTimeField(null=True, verbose_name=_('Phase 2 Start Date'))
    phase2_end_date = models.DateTimeField(null=True, verbose_name=_('Phase 2 End Date'))
    phase3_start_date = models.DateTimeField(null=True, verbose_name=_('Phase 3 Start Date'))
    phase3_end_date = models.DateTimeField(null=True, verbose_name=_('Phase 3 End Date'))
    phase4_start_date = models.DateTimeField(null=True, verbose_name=_('Phase 4 Start Date'))
    phase4_end_date = models.DateTimeField(null=True, verbose_name=_('Phase 4 End Date'))
    # results_date = models.DateTimeField(null=True, blank=False, verbose_name=_('Results Announcement Date'))
    high_school_gpa_weight = models.FloatField(null=True, blank=False, verbose_name=_('High School GPA Weight'))
    qudrat_score_weight = models.FloatField(null=True, blank=False, verbose_name=_('Qudrat Score Weight'))
    tahsili_score_weight = models.FloatField(null=True, blank=False, verbose_name=_('Tahsili Score Weight'))
    cutoff_point = models.FloatField(null=True, blank=True, verbose_name=_('Cutoff Point'))

    class Meta:
        verbose_name = _('Admission Semester')
        verbose_name_plural = _('Admission: Admission Semesters')

    def __str__(self):
        return self.semester_name

    @staticmethod
    def get_phase1_active_semester():
        try:
            now = timezone.now()
            sem = AdmissionSemester.objects.filter(phase1_start_date__lte=now, phase1_end_date__gte=now).first()
            return sem
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def get_phase2_active_semester(user):
        now = timezone.now()
        sem = AdmissionSemester.objects.filter(phase2_start_date__lte=now, phase2_end_date__gte=now).first()

        # if phase 2 expired globally but the student is given an exception
        if not sem:
            if user and user.phase2_start_date and user.phase2_end_date and \
                                    user.phase2_start_date <= now <= user.phase2_end_date:
                sem = user.semester

        return sem

    @staticmethod
    def get_phase3_active_semester(user):
        now = timezone.now()
        sem = AdmissionSemester.objects.filter(phase3_start_date__lte=now, phase3_end_date__gte=now).first()

        # if phase 3 expired globally but the student is given an exception
        if not sem:
            if user and user.phase3_start_date and user.phase3_end_date and \
                                    user.phase3_start_date <= now <= user.phase3_end_date:
                sem = user.semester

        return sem

    @staticmethod
    def get_phase4_active_semester():
        now = timezone.now()
        sem = AdmissionSemester.objects.filter(phase4_start_date__lte=now, phase4_end_date__gte=now).first()

        return sem

    @staticmethod
    def check_if_phase1_is_active():
        # cache if semester phase1 is active for 15 mins
        if cache.get('phase1_active') is None:
            sem = AdmissionSemester.get_phase1_active_semester()
            if sem:
                cache.set('phase1_active', True, 15 * 60)
                return True
            else:
                return False
        else:
            if cache.get('phase1_active'):
                return True
            else:
                return False

    @staticmethod
    def get_semesters_choices(add_dashes=True):
        try:
            choices = AdmissionSemester.objects.all()

            ch = [(o.pk, str(o)) for o in choices]
            if add_dashes:
                ch.insert(0, ('', '---------'))

            return ch
        except:  # was OperationalError and happened when db doesn't exist yet but later changed it to general except to catch an weird exceptions like ProgrammingError
            return [('--', '--')]


class KFUPMIDsPool(models.Model):
    semester = models.ForeignKey(
        'AdmissionSemester',
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        related_name='semester_ids',
        verbose_name=_('Admission Semester'),
        db_index=True,
    )
    kfupm_id = models.PositiveIntegerField(unique=True, null=True, blank=True, verbose_name=_('KFUPM ID'))

    class Meta:
        verbose_name_plural = _('Registrar: KFUPM ID Pools')

    def __str__(self):
        return str(self.kfupm_id)

    @property
    def assigned_student(self):
        try:
            student = User.objects.get(kfupm_id=self.kfupm_id)
            return '%s - (%s)' % (str(student), student.username)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def get_next_available_id():
        kid = KFUPMIDsPool.objects.exclude(kfupm_id__in=User.objects.filter(kfupm_id__isnull=False)
                                           .values_list('kfupm_id', flat=True)).order_by('?').first()
        if kid:
            return kid.kfupm_id
        else:
            return 0


class RegistrationStatus(models.Model):
    status_ar = models.CharField(max_length=50, verbose_name=_('Status (Arabic)'))
    status_en = models.CharField(max_length=50, verbose_name=_('Status (English)'))
    status_code = models.CharField(max_length=20, null=True, blank=False, unique=True, )

    @property
    def registration_status(self):
        lang = translation.get_language()
        if lang == "ar":
            return self.status_ar
        else:
            return self.status_en

    def __str__(self):
        return self.registration_status

    class Meta:
        verbose_name_plural = _('Admission: Registration Status')


class RegistrationStatusMessage(models.Model):
    status_message_ar = models.CharField(max_length=500, verbose_name=_('Registration Status Message AR'))
    status_message_en = models.CharField(max_length=500, verbose_name=_('Registration Status Message EN'))
    status_message_code = models.CharField(max_length=20, null=True, blank=False, unique=True, )
    status = models.ForeignKey(
        'RegistrationStatus',
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        related_name='status_messages'
    )

    class Meta:
        verbose_name_plural = _('Admission: Registration Status Messages')

    @property
    def registration_status_message(self):
        lang = translation.get_language()
        if lang == "ar":
            return self.status_message_ar
        else:
            return self.status_message_en

    def __str__(self):
        return self.registration_status_message

    @staticmethod
    def get_registration_status_choices(add_dashes=True):
        try:
            choices = RegistrationStatusMessage.objects.all()

            ch = [(o.id, str(o.status) + ' - ' + str(o)) for o in choices]
            if add_dashes:
                ch.insert(0, ('', '---------'))

            return ch
        except:  # was OperationalError and happened when db doesn't exist yet but later changed it to general except to catch an weird exceptions like ProgrammingError
            return [('--', '--')]

    @staticmethod
    def get_status_applied():
        try:
            return RegistrationStatus.objects.get(status_code='APPLIED').status_messages. \
                get(status_message_code='APPLIED')
        except ObjectDoesNotExist:
            return

    @staticmethod
    def get_status_non_saudi():
        try:
            return RegistrationStatus.objects.get(status_code='APPLIED').status_messages. \
                get(status_message_code='NON-SAUDI')
        except ObjectDoesNotExist:
            return

    @staticmethod
    def get_status_old_high_school():
        try:
            return RegistrationStatus.objects.get(status_code='REJECTED').status_messages. \
                get(status_message_code='OLD-HS')
        except ObjectDoesNotExist:
            return

    @staticmethod
    def get_status_girls():
        try:
            return RegistrationStatus.objects.get(status_code='REJECTED').status_messages. \
                get(status_message_code='GIRLS')
        except ObjectDoesNotExist:
            return

    @staticmethod
    def get_status_withdrawn():
        try:
            return RegistrationStatus.objects.get(status_code='WITHDRAWN').status_messages.first()
        except ObjectDoesNotExist:
            return

    @staticmethod
    def get_status_admitted():
        try:
            return RegistrationStatus.objects.get(status_code='ADMITTED').status_messages.first()
        except ObjectDoesNotExist:
            return

    @staticmethod
    def get_status_duplicate():
        try:
            return RegistrationStatus.objects.get(status_code='SUSPENDED') \
                .status_messages.get(status_message_code='DUPLICATE')
        except ObjectDoesNotExist:
            return

    @staticmethod
    def get_status_confirmed():
        try:
            return RegistrationStatus.objects.get(status_code='PARTIALLY-ADMITTED') \
                .status_messages.get(status_message_code='CONFIRMED')
        except ObjectDoesNotExist:
            return

    @staticmethod
    def get_status_confirmed_non_saudi():
        try:
            return RegistrationStatus.objects.get(status_code='PARTIALLY-ADMITTED') \
                .status_messages.get(status_message_code='CONFIRMED-N')
        except ObjectDoesNotExist:
            return


class Lookup(models.Model):
    lookup_type = models.CharField(max_length=20, null=True, blank=False, db_index=True)
    lookup_value_ar = models.CharField(max_length=100, null=True, blank=False)
    lookup_value_en = models.CharField(max_length=100, null=True, blank=False)
    show = models.BooleanField(verbose_name=_('Show'), default=True)
    display_order = models.PositiveSmallIntegerField(null=True, verbose_name=_('Display Order'))

    class Meta:
        verbose_name_plural = _('Admission: Look ups')
        ordering = ['lookup_type', '-display_order']

    @property
    def lookup_value(self):
        lang = translation.get_language()
        if lang == "ar":
            return self.lookup_value_ar
        else:
            return self.lookup_value_en

    def __str__(self):
        return self.lookup_value

    @staticmethod
    def get_lookup_choices(lookup_type, add_dashes=True):
        try:
            choices = Lookup.objects.filter(
                show=True,
                lookup_type=lookup_type)

            ch = [(o.lookup_value_ar, str(o)) for o in choices]
            if add_dashes:
                ch.insert(0, ('', '---------'))

            return ch
        except:  # was OperationalError and happened when db doesn't exist yet but later changed it to general except to catch an weird exceptions like ProgrammingError
            return [('--', '--')]


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
        ordering = ['-display_order']
        verbose_name_plural = _('Admission: Cities')


class DeniedStudent(models.Model):
    government_id = models.CharField(max_length=12, verbose_name=_('Government ID'), db_index=True)
    student_name = models.CharField(max_length=400, verbose_name=_('Student Name'))
    message = models.CharField(max_length=400, verbose_name=_('Message'))
    university_code = models.CharField(max_length=10, verbose_name=_('University Code'))
    semester = models.ForeignKey(
        'AdmissionSemester',
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        related_name='denied_students',
        db_index=True,
    )
    last_trial_date = models.DateTimeField(null=True, blank=True, verbose_name=_('Last Trial Date'))
    trials_count = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=_('Count Trial'))

    class Meta:
        verbose_name_plural = _('Admission: Denied Students')

    def __str__(self):
        return self.student_name + ' (' + self.government_id + ')'

    @staticmethod
    def check_if_student_is_denied(govid):
        activeSem = AdmissionSemester.get_phase1_active_semester()
        denied = activeSem.denied_students.filter(government_id=govid).first()

        if denied:
            denied.last_trial_date = timezone.now()
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

    class Meta:
        verbose_name_plural = _('Admission: Distinguished Students')

    def __str__(self):
        return self.student_name + ' (' + self.government_id + ')'


class GraduationYear(models.Model):
    graduation_year_en = models.CharField(max_length=50, verbose_name=_('Graduation Year (English)'))
    graduation_year_ar = models.CharField(max_length=50, verbose_name=_('Graduation Year (Arabic)'))
    description = models.CharField(max_length=200, verbose_name=_('Description'))
    show = models.BooleanField(verbose_name=_('Show'), default=True)
    display_order = models.PositiveSmallIntegerField(null=True, verbose_name=_('Display Order'))

    class Meta:
        ordering = ['-display_order']
        verbose_name_plural = _('Admission: Graduation Years')

    @staticmethod
    def get_graduation_year_choices(add_dashes=True):
        try:
            choices = GraduationYear.objects.filter(show=True)

            ch = [(o.id, str(o)) for o in choices]
            if add_dashes:
                ch.insert(0, ('', '---------'))

            return ch
        except:  # was OperationalError and happened when db doesn't exist yet but later changed it to general except to catch an weird exceptions like ProgrammingError
            return [('--', '--')]

    @staticmethod
    def get_graduation_year(academic_hijri_year):
        try:
            return GraduationYear.objects.get(description=academic_hijri_year)
        except ObjectDoesNotExist:
            return None

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

    @staticmethod
    def get_nationality_choices(add_dashes=True):
        try:
            choices = Nationality.objects.filter(show=True)

            ch = [(o.id, str(o)) for o in choices]
            if add_dashes:
                ch.insert(0, ('', '---------'))

            return ch
        except:  # was OperationalError and happened when db doesn't exist yet but later changed it to general except to catch an weird exceptions like ProgrammingError
            return [('--', '--')]

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
        ordering = ['display_order', 'nationality_en']
        verbose_name_plural = _('Admission: Nationalities')


class Agreement(models.Model):
    semester = models.ForeignKey(
        'AdmissionSemester',
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        related_name='agreement',
        verbose_name='Semester',
    )
    agreement_type = models.CharField(max_length=100, null=True, blank=False, verbose_name=_('Agreement Type'))
    agreement_header_ar = models.TextField(max_length=2000, null=True, blank=True,
                                           verbose_name=_('Agreement Header (Arabic)'))
    agreement_header_en = models.TextField(max_length=2000, null=True, blank=True,
                                           verbose_name=_('Agreement Header (English)'))
    agreement_footer_ar = models.TextField(max_length=2000, null=True, blank=True,
                                           verbose_name=_('Agreement Footer (Arabic)'))
    agreement_footer_en = models.TextField(max_length=2000, null=True, blank=True,
                                           verbose_name=_('Agreement Footer (English)'))

    class Meta:
        verbose_name_plural = _('Admission and Student Affairs: Agreements')

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
        related_name='items',
    )
    agreement_text_ar = models.TextField(max_length=2000, verbose_name=_('Agreement Text (Arabic)'))
    agreement_text_en = models.TextField(max_length=2000, verbose_name=_('Agreement Text (English)'))
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
        verbose_name_plural = _('Admission and Student Affairs: Agreement Items')
        ordering = ['agreement', '-display_order']


# Auxiliary table in the database for BI reports
class Aux1To100(models.Model):
    counter = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Counter'))


# Important dates model for Qabool. It should display as list in the homepage sidebar.
class ImportantDateSidebar(models.Model):
    title_ar = models.CharField(max_length=200, verbose_name=_('Arabic Title'))
    title_en = models.CharField(max_length=200, verbose_name=_('English Title'))
    description_ar = models.CharField(max_length=300, null=True, verbose_name=_('Arabic Description'))
    description_en = models.CharField(max_length=300, null=True, verbose_name=_('English Description'))
    show = models.BooleanField(verbose_name=_('Show'), default=True)
    display_order = models.PositiveSmallIntegerField(null=True, verbose_name=_('Display Order'))

    @property
    def title(self):
        lang = translation.get_language()
        if lang == "ar":
            return self.title_ar
        else:
            return self.title_en

    @property
    def description(self):
        lang = translation.get_language()
        if lang == "ar":
            return self.description_ar
        else:
            return self.description_en

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['display_order']
        verbose_name_plural = _('Admission: Important Date Sidebar')


class TarifiReceptionDate(models.Model):
    semester = models.ForeignKey(
        'AdmissionSemester',
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        related_name='tarifi_reception_dates',
        verbose_name='Semester',
    )
    reception_date = models.CharField(max_length=600, null=True, blank=False, verbose_name=_('Reception Date'))
    slots = models.PositiveSmallIntegerField(null=True, blank=False, default=300, verbose_name=_('Slots'))
    slot_start_date = models.DateTimeField(null=True, blank=False, verbose_name=_('Start Date'))
    slot_end_date = models.DateTimeField(null=True, blank=False, verbose_name=_('End Date'))
    show = models.BooleanField(verbose_name=_('Show'), default=True)
    display_order = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=_('Display Order'))

    class Meta:
        verbose_name_plural = _('Tarifi: Tarifi Reception Dates')
        ordering = ['slot_start_date']

    @property
    def remaining_slots(self):
        return self.slots - User.objects.filter(tarifi_week_attendance_date=self.pk,
                                                status_message=RegistrationStatusMessage.get_status_admitted()).count()

    @staticmethod
    def get_all_available_slots(user, add_dashes=True):
        try:
            choices = TarifiReceptionDate.objects.filter(semester=AdmissionSemester.get_phase3_active_semester(user))

            ch = [(o.id, str(o)) for o in choices if o.remaining_slots > 0]
            if add_dashes:
                ch.insert(0, ('', '---------'))

            return ch
        except:  # was OperationalError and happened when db doesn't exist yet but later changed it to general except to catch an weird exceptions like ProgrammingError
            return [('--', '--')]

    def __str__(self):
        return self.reception_date

