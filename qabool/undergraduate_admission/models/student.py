from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django_countries.fields import CountryField

from find_roommate.models import RoommateRequest
from undergraduate_admission.media_handlers import upload_location_govid, upload_location_birth, \
    upload_location_mother_govid, upload_location_passport, upload_location_certificate, \
    upload_location_picture, upload_location_courses, upload_location_withdrawal_proof, \
    upload_location_driving_license, upload_location_vehicle_registration, upload_bank_account_identification
from undergraduate_admission.validators import validate_file_extension, validate_image_extension
from .supporting_models import AdmissionSemester, RegistrationStatus, VerificationIssues

User = settings.AUTH_USER_MODEL


class AdmissionRequest(models.Model):
    class Gender:
        MALE = 'M'
        FEMALE = 'F'

        @classmethod
        def choices(cls):
            return (
                (cls.MALE, _('Male')),
                (cls.FEMALE, _('Female')),
            )

    class HighSchoolSystems:
        PUBLIC = 'PUBLIC'
        PRIVATE = 'PRIVATE'
        INTERNATIONAL = 'INTERNATIONAL'

        @classmethod
        def choices(cls):
            return (
                (cls.PUBLIC, _('Public')),
                (cls.PRIVATE, _('Private')),
                (cls.INTERNATIONAL, _('International')),
            )

    user = models.ForeignKey(User, related_name='admission_requests', null=True, blank=True,
                             verbose_name=_('Associated User'),
                             on_delete=models.SET_NULL,
                             help_text=_('The user associated with this admission request.'))
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
        'RegistrationStatus',
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        verbose_name=_('Message Status'),
    )

    # region Notes Fields
    student_notes = models.TextField(null=True, blank=True, max_length=500, verbose_name=_('Student Notes'))
    admission_note = models.CharField(null=True, blank=True, max_length=500, verbose_name=_('Admission Note'))
    admission_note2 = models.CharField(null=True, blank=True, max_length=500, verbose_name=_('Admission Note 2'))
    admission_note3 = models.CharField(null=True, blank=True, max_length=500, verbose_name=_('Admission Note 3'))
    # endregion

    # region Names Fields
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
    # endregion

    # region Personal Info Fields
    nationality = CountryField(
        null=True, blank=False,
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
    mother_gov_id_file = models.FileField(
        null=True,
        blank=True,
        max_length=100,
        verbose_name=_('Mother Government ID'),
        upload_to=upload_location_mother_govid,
        validators=[validate_file_extension],
    )
    birthday = models.DateField(null=True, blank=True, verbose_name=_('Birthday'))
    birthday_ah = models.CharField(null=True, blank=True, max_length=50, verbose_name=_('Birthday Hijri'))
    birth_place = models.CharField(null=True,
                                   blank=True,
                                   max_length=100,
                                   verbose_name=_('Birth Place'),
                                   help_text=_('Country and city. e.g. Saudi Arabia Jeddah'))
    birth_certificate = models.FileField(
        null=True,
        blank=True,
        max_length=100,
        verbose_name=_('Birth Date Certificate'),
        upload_to=upload_location_birth,
        validators=[validate_file_extension],
    )
    mobile = models.CharField(
        null=True,
        blank=False,
        max_length=12,
        verbose_name=_('Mobile'),
        help_text=_(
            'Mobile number should be of this format "9665xxxxxxxx". Use English numerals only. Please make sure to '
            'activate promotional messages from your mobile provider.'),
        validators=[
            RegexValidator(
                '^(9665|٩٦٦٥)\d{8}$',
                message=_('You have entered an invalid mobile number')
            ),
        ],
        db_index=True,
    )
    phone = models.CharField(null=True,
                             blank=True,
                             max_length=50,
                             verbose_name=_('Phone'),
                             help_text=_('With country and area code. e.g. 966138602722'), )
    kfupm_id = models.PositiveIntegerField(unique=True, null=True, blank=True, verbose_name=_('KFUPM ID'))
    personal_picture = models.FileField(
        null=True,
        blank=True,
        max_length=100,
        verbose_name=_('Personal Picture'),
        upload_to=upload_location_picture,
        validators=[validate_image_extension],
    )
    gender = models.CharField(choices=Gender.choices(), max_length=128, default=Gender.MALE, verbose_name=_('Gender'))
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
    # endregion

    # region Scores Fields
    qudrat_score = models.FloatField(null=True, blank=True, verbose_name=_('Qudrat Score (Qiyas)'),
                                     validators=[MinValueValidator(1), MaxValueValidator(100)], )
    tahsili_score = models.FloatField(null=True, blank=True, verbose_name=_('Tahsili Score (Qiyas)'),
                                      validators=[MinValueValidator(1), MaxValueValidator(100)], )
    high_school_gpa = models.FloatField(null=True, blank=True, verbose_name=_('High School GPA (Ministry)'),
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
    # endregion

    # region Government ID Fields
    government_id_file = models.FileField(
        null=True,
        blank=True,
        max_length=100,
        verbose_name=_('Government ID File'),
        upload_to=upload_location_govid,
        validators=[validate_file_extension],
    )
    government_id_type = models.CharField(_('Government ID Type'), null=True, blank=True, max_length=100)
    government_id_issue = models.DateField(null=True, blank=True, verbose_name=_('Government ID Issue Date'))
    government_id_expiry = models.CharField(null=True, blank=True, max_length=20,
                                            verbose_name=_('Government ID Expiry Date'))
    government_id_place = models.CharField(null=True, blank=True, max_length=50,
                                           verbose_name=_('Government ID Place of Issue'))
    # endregion

    # region Passport Fields
    passport_number = models.CharField(null=True, blank=True, max_length=50, verbose_name=_('Passport Number'))
    passport_place = models.CharField(null=True, blank=True, max_length=50, verbose_name=_('Passport Place of Issue '))
    passport_expiry = models.DateField(null=True, blank=True, verbose_name=_('Passport Expiry Date'))
    passport_file = models.FileField(
        null=True,
        blank=True,
        max_length=100,
        verbose_name=_('Upload Passport'),
        upload_to=upload_location_passport,
        validators=[validate_file_extension],
    )
    # endregion

    # region High School fields
    high_school_graduation_year = models.ForeignKey(
        'GraduationYear',
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        verbose_name=_('Graduation Year'),
    )
    high_school_id = models.CharField(null=True, blank=True, max_length=20, verbose_name=_('High School ID'))
    high_school_name = models.CharField(null=True, blank=True, max_length=100,
                                        verbose_name=_('High School Name (Arabic)'))
    high_school_name_en = models.CharField(null=True, blank=True, max_length=100,
                                           verbose_name=_('High School Name (English)'))
    high_school_system = models.CharField(null=True, blank=True, max_length=100, verbose_name=_('High School System'),
                                          choices=HighSchoolSystems.choices())
    high_school_major_code = models.CharField(null=True, blank=True, max_length=20,
                                              verbose_name=_('High School Major Code'))
    high_school_major_name = models.CharField(null=True, blank=True, max_length=100,
                                              verbose_name=_('High School Major Name (Arabic)'))
    high_school_major_name_en = models.CharField(null=True, blank=True, max_length=100,
                                                 verbose_name=_('High School Major Name (English)'))
    high_school_province_code = models.CharField(null=True, blank=True, max_length=20,
                                                 verbose_name=_('High School Province Code'))
    high_school_province = models.CharField(null=True, blank=True, max_length=100,
                                            verbose_name=_('High School Province (Arabic)'))
    high_school_province_en = models.CharField(null=True, blank=True, max_length=100,
                                               verbose_name=_('High School Province (English)'))
    high_school_city_code = models.CharField(null=True, blank=True, max_length=20,
                                             verbose_name=_('High School City Code'))
    high_school_city = models.CharField(null=True, blank=True, max_length=100,
                                        verbose_name=_('High School City (Arabic)'))
    high_school_city_en = models.CharField(null=True, blank=True, max_length=100,
                                           verbose_name=_('High School City (English)'))
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
    # endregion

    # region Withdrawal Fields
    withdrawal_university = models.CharField(null=True,
                                             blank=True,
                                             max_length=100,
                                             verbose_name=_('Withdrew To University'))
    withdrawal_reason = models.CharField(null=True,
                                         blank=True,
                                         max_length=500,
                                         verbose_name=_('Withdrawal Reason'))
    withdrawal_proof_letter = models.FileField(
        null=True,
        blank=True,
        max_length=100,
        verbose_name=_('Withdrawal Proof Letter'),
        upload_to=upload_location_withdrawal_proof,
        validators=[validate_file_extension],
    )
    withdrawal_date = models.DateTimeField(null=True, blank=True, verbose_name=_('Withdrawal Date'))
    # endregion

    # region Guardian Fields
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
    # endregion

    # region Relative Fields
    relative_name = models.CharField(null=True, blank=True, max_length=50, verbose_name=_('Relative Name'))
    relative_relation = models.CharField(null=True, blank=True, max_length=50, verbose_name=_('Relative Relation'))
    relative_phone = models.CharField(null=True,
                                      blank=True,
                                      max_length=50,
                                      verbose_name=_('Relative Mobile'),
                                      help_text=_('With country and area code. e.g. 966138602722'), )
    relative_po_box = models.CharField(null=True, blank=True, max_length=50, verbose_name=_('Relative PO Box'))
    relative_postal_code = models.CharField(null=True,
                                            blank=True,
                                            max_length=50,
                                            verbose_name=_('Relative Postal Code'))
    relative_city = models.CharField(null=True, blank=True, max_length=50, verbose_name=_('Relative City'))
    relative_job = models.CharField(null=True, blank=True, max_length=50, verbose_name=_('Relative Work'))
    relative_employer = models.CharField(null=True, blank=True, max_length=50, verbose_name=_('Relative Employer'))
    # endregion

    # region Vehicle Fields
    have_a_vehicle = models.BooleanField(
        verbose_name=_('Do you have a vehicle you want to register?'),
        default=False,
        help_text=_('This will let us help you better to get you a permit to enter campus.'),
    )
    vehicle_plate_no = models.CharField(null=True, blank=True, max_length=100, verbose_name=_('Vehicle Plate No.'))
    vehicle_owner = models.CharField(null=True, blank=True, max_length=100, verbose_name=_('Vehicle Owner'))
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
    # endregion

    # region Bank Fields
    bank_name = models.CharField(null=True, blank=True, max_length=100, verbose_name=_('Bank Name'))
    bank_account = models.CharField(null=True, blank=True, max_length=50, verbose_name=_('Your IBAN'),
                                    help_text=_('Your International Bank Account Number (IBAN) for your own Saudi bank '
                                                'account. Your IBAN format should be SA followed by 22 digits.'),
                                    validators=[
                                        RegexValidator(
                                            '^(SA)\d{22}$',
                                            message=_('You have entered an invalid IBAN')
                                        ),
                                    ], )
    bank_account_identification_file = models.FileField(
        null=True,
        blank=True,
        max_length=100,
        verbose_name=_('Bank Account Identification File'),
        upload_to=upload_bank_account_identification,
        validators=[validate_file_extension],
    )
    # endregion

    # region Important Dates Field
    admission_letter_print_date = models.DateTimeField(null=True,
                                                       blank=True,
                                                       verbose_name=_('Admission Letter Print Date'))
    medical_report_print_date = models.DateTimeField(null=True,
                                                     blank=True,
                                                     verbose_name=_('Medical Report Print Date'))
    request_date = models.DateTimeField(null=True, auto_now_add=True, verbose_name=_('Request Date'))
    phase2_start_date = models.DateTimeField(null=True, blank=True, verbose_name=_('Phase 2 Start Date'))
    phase2_end_date = models.DateTimeField(null=True, blank=True, verbose_name=_('Phase 2 End Date'))
    phase3_start_date = models.DateTimeField(null=True, blank=True, verbose_name=_('Phase 3 Start Date'))
    phase3_end_date = models.DateTimeField(null=True, blank=True, verbose_name=_('Phase 3 End Date'))
    phase2_submit_date = models.DateTimeField(null=True, blank=True, verbose_name=_('Phase 2 Submit Date'))
    phase2_re_upload_date = models.DateTimeField(null=True, blank=True, verbose_name=_('Phase 2 Re-Upload Date'))
    phase3_submit_date = models.DateTimeField(null=True, blank=True, verbose_name=_('Phase 3 Submit Date'))
    # endregion

    # region Verification Fields
    verification_committee_member = models.CharField(null=True, blank=True, max_length=50,
                                                     verbose_name=_('Assigned Committee Member'))
    verification_issues = models.ManyToManyField('VerificationIssues', blank=True, related_name='student_issues',
                                                 verbose_name=_('Verification Issues'))
    verification_notes = models.CharField(null=True, blank=True, max_length=500, verbose_name=_('Verification Note'))
    # endregion

    # region Tarifi Week Fields
    eligible_for_housing = models.NullBooleanField(verbose_name=_('Eligible For Housing'))
    tarifi_week_attendance_date = models.ForeignKey('TarifiReceptionDate',
                                                    verbose_name=_('Tarifi Week Attendance Date'),
                                                    on_delete=models.SET_NULL,
                                                    null=True,
                                                    blank=True, )
    # endregion

    # region Yesser Data Fields
    yesser_high_school_data_dump = models.TextField(_('Fetched Yesser High School Data Dump'), null=True, blank=True, )
    yesser_qudrat_data_dump = models.TextField(_('Fetched Yesser Qudrat Data Dump'), null=True, blank=True, )
    yesser_tahsili_data_dump = models.TextField(_('Fetched Yesser Tahsili Data Dump'), null=True, blank=True, )

    # endregion

    class Meta:
        verbose_name = _('Admission Request')
        verbose_name_plural = _('Admission Requests')
        unique_together = ('user', 'semester')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from ..utils import add_validators_to_arabic_and_english_names
        add_validators_to_arabic_and_english_names(self._meta.fields)

    def get_verification_status(self):
        return self.verification_status

    get_verification_status.short_description = _('Issues With Uploaded Docs')

    def get_student_full_name(self):
        if self.first_name_ar or self.second_name_ar or self.family_name_ar:
            return '%s %s %s %s' % (self.first_name_ar,
                                    self.second_name_ar, self.third_name_ar, self.family_name_ar)
        elif self.student_full_name_ar:
            return self.student_full_name_ar
        else:
            return 'ERROR: You do NOT have a name. Contact the admins about this ASAP'

    get_student_full_name.short_description = _('Full Name')

    def get_student_full_name_and_source(self):
        if self.first_name_ar or self.second_name_ar or self.family_name_ar:
            return '(Yesser) %s %s %s %s' % (self.first_name_ar, self.second_name_ar,
                                             self.third_name_ar, self.family_name_ar)
        elif self.student_full_name_ar:
            return '(Student) %s' % self.student_full_name_ar
        else:
            return 'ERROR: You do NOT have a name. Contact the admins about this ASAP'

    get_student_full_name_and_source.short_description = _('Full Name and Source')

    def are_arabic_names_matching(self):
        return self.student_full_name_ar == '%s %s %s %s' % (self.first_name_ar, self.second_name_ar,
                                                             self.third_name_ar, self.family_name_ar)

    def are_english_names_matching(self):
        return self.student_full_name_en == '%s %s %s %s' % (self.first_name_en, self.second_name_en,
                                                             self.third_name_en, self.family_name_en)

    def get_student_phase(self):
        try:
            return self.status_message.general_status
        except:
            return RegistrationStatus.GeneralStatuses.REJECTED

    def get_student_phase_display(self):
        try:
            return self.status_message.get_general_status_display()
        except:
            return RegistrationStatus.GeneralStatuses.REJECTED

    def get_student_status_display(self):
        try:
            return self.status_message.registration_status_message
        except:
            return RegistrationStatus.GeneralStatuses.REJECTED

    @property
    def student_type(self):
        student_type = 'S'

        if self.nationality:
            if self.nationality != 'SA' and self.saudi_mother:
                student_type = 'M'
            elif self.nationality != 'SA':
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

    @property
    def government_id(self):
        try:
            return self.user.username
        except:
            return 'None'

    # region the can's and cant's
    def can_confirm(self):
        return ((self.status_message == RegistrationStatus.get_status_partially_admitted() or
                 # self.status_message == RegistrationStatus.get_status_partially_admitted_non_saudi or
                 self.status_message == RegistrationStatus.get_status_partially_admitted_transfer())
                and AdmissionSemester.get_phase2_active_semester(self))

    def can_see_result(self):
        return self.get_student_phase() in [RegistrationStatus.GeneralStatuses.PARTIALLY_ADMITTED,
                                            RegistrationStatus.GeneralStatuses.REJECTED]

    def can_print_docs(self):
        return (self.status_message in [RegistrationStatus.get_status_admitted_final(),
                                        RegistrationStatus.get_status_admitted_non_saudi_final()]
                and self.tarifi_week_attendance_date)

    def can_withdraw(self):
        now = timezone.now()
        return ((self.get_student_phase() == RegistrationStatus.GeneralStatuses.ADMITTED
                 or self.status_message == RegistrationStatus.get_status_confirmed())
                and now <= self.semester.withdrawal_deadline)

    def can_print_withdrawal_letter(self):
        return self.get_student_phase() == RegistrationStatus.GeneralStatuses.WITHDRAWN

    def can_finish_phase3(self):
        return (self.status_message in [RegistrationStatus.get_status_admitted(),
                                        RegistrationStatus.get_status_admitted_non_saudi()]
                and not self.tarifi_week_attendance_date
                and AdmissionSemester.get_phase3_active_semester(self))

    def has_pic(self):
        return self.get_student_phase() in [RegistrationStatus.GeneralStatuses.PARTIALLY_ADMITTED,
                                            RegistrationStatus.GeneralStatuses.ADMITTED]

    def can_see_kfupm_id(self):
        return self.get_student_phase() == RegistrationStatus.GeneralStatuses.ADMITTED and self.kfupm_id

    def can_see_housing(self):
        return (self.get_student_phase() == RegistrationStatus.GeneralStatuses.ADMITTED and self.eligible_for_housing
                and AdmissionSemester.get_phase4_active_semester())

    def can_search_in_housing(self):
        try:
            return self.can_see_housing() and self.housing_user.searchable
        except ObjectDoesNotExist:
            return False

    def can_re_upload_picture(self):
        return (self.get_student_phase() == RegistrationStatus.GeneralStatuses.PARTIALLY_ADMITTED
                and self.verification_issues.filter(
                    related_field=VerificationIssues.RelatedFields.PERSONAL_PICTURE).exists())

    def can_re_upload_docs(self):
        return (self.get_student_phase() == RegistrationStatus.GeneralStatuses.PARTIALLY_ADMITTED
                and self.verification_issues.exclude(
                    related_field=VerificationIssues.RelatedFields.PERSONAL_PICTURE).exists())

    def can_upload_withdrawal_proof(self):
        return self.status_message == RegistrationStatus.get_status_duplicate()

    def can_edit_phase1_info(self):
        return (self.get_student_phase() == RegistrationStatus.GeneralStatuses.APPLIED
                and AdmissionSemester.check_if_phase1_is_active())

    def can_access_phase3(self):
        return (self.status_message in [RegistrationStatus.get_status_admitted(),
                                        RegistrationStatus.get_status_admitted_non_saudi()]
                and AdmissionSemester.get_phase3_active_semester(self))

    def can_edit_contact_info(self):
        return self.get_student_phase() not in [
            RegistrationStatus.GeneralStatuses.REJECTED,
            RegistrationStatus.GeneralStatuses.WITHDRAWN,
            RegistrationStatus.GeneralStatuses.SUSPENDED,
        ] and not self.can_edit_phase1_info()
    # endregion

    def pending_housing_roommate_requests_count(self):
        return RoommateRequest.objects.filter(requested_user=self,
                                              status=RoommateRequest.RequestStatuses.PENDING).count()

    @staticmethod
    def get_distinct_high_school_city(add_dashes=True):
        try:
            choices = AdmissionRequest.objects.filter(eligible_for_housing=True, housing_user__searchable=True). \
                order_by().values('high_school_city').distinct()

            ch = [(o['high_school_city'], o['high_school_city']) for o in choices]
            if add_dashes:
                ch.insert(0, ('', '---------'))

            return ch
        except:  # was OperationalError and happened when db doesn't exist yet but later changed it to general except to catch an weird exceptions like ProgrammingError
            return [('--', '--')]

    def __str__(self):
        return self.get_student_full_name()


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
            student = AdmissionRequest.objects.get(kfupm_id=self.kfupm_id)
            return '%s - (%s)' % (str(student), student.user.username)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def get_next_available_id(student):
        if student:
            kid = KFUPMIDsPool.objects.filter(semester=student.semester) \
                .exclude(kfupm_id__in=AdmissionRequest.objects.filter(kfupm_id__isnull=False)
                         .values_list('kfupm_id', flat=True)).order_by('?').first()

            if kid:
                return kid.kfupm_id
            else:
                return 0
        else:
            return 0


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


# TODO: to be removed
class DistinguishedStudent(models.Model):
    government_id = models.CharField(max_length=12, verbose_name=_('Government ID'))
    student_name = models.CharField(max_length=400, verbose_name=_('Student Name'))
    city = models.CharField(max_length=400, verbose_name=_('City'))
    attended = models.BooleanField(verbose_name=_('Attended'), default=True)

    class Meta:
        verbose_name_plural = _('Admission: Distinguished Students')

    def __str__(self):
        return self.student_name + ' (' + self.government_id + ')'


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
        verbose_name_plural = _('Orientation Week: Schedule')
        ordering = ['slot_start_date']

    @property
    def remaining_slots(self):
        return self.slots - AdmissionRequest.objects.filter(
            tarifi_week_attendance_date=self.pk,
            status_message=RegistrationStatus.get_status_admitted_final()
        ).count()

    @staticmethod
    def get_all_available_slots(user, add_dashes=True):
        try:
            choices = TarifiReceptionDate.objects.filter(semester=AdmissionSemester.get_phase3_active_semester(user),
                                                         show=True)

            ch = [(o.id, str(o)) for o in choices if o.remaining_slots > 0]
            if add_dashes:
                ch.insert(0, ('', '---------'))

            return ch
        except:  # was OperationalError and happened when db doesn't exist yet but later changed it to general except to catch an weird exceptions like ProgrammingError
            return [('--', '--')]

    def __str__(self):
        return self.reception_date
