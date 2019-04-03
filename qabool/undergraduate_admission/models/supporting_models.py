from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import timezone
from django.utils import translation
from django.utils.translation import ugettext_lazy as _


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
    withdrawal_deadline = models.DateTimeField(null=True, blank=False, verbose_name=_('Withdrawal Deadline'))
    high_school_gpa_weight = models.FloatField(null=True, blank=False, verbose_name=_('High School GPA Weight'))
    qudrat_score_weight = models.FloatField(null=True, blank=False, verbose_name=_('Qudrat Score Weight'))
    tahsili_score_weight = models.FloatField(null=True, blank=False, verbose_name=_('Tahsili Score Weight'))
    cutoff_point = models.FloatField(null=True, blank=True, verbose_name=_('Cutoff Point'))
    active = models.BooleanField(verbose_name=_('Active Semester'), default=True,
                                 help_text=_('Indicator of the current active semester. This will be used in the '
                                             'admin-side and committee pages'))

    class Meta:
        verbose_name = _('Admission Semester')
        verbose_name_plural = _('Admission: Admission Semesters')

    def __str__(self):
        return self.semester_name

    @staticmethod
    def get_active_semester():
        try:
            sem = AdmissionSemester.objects.filter(active=True).first()
            return sem
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def get_phase1_active_semester():
        try:
            now = timezone.now()
            sem = AdmissionSemester.objects.filter(phase1_start_date__lte=now, phase1_end_date__gte=now).first()
            return sem
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def get_phase2_active_semester(admission_request):
        now = timezone.now()
        sem = AdmissionSemester.objects.filter(phase2_start_date__lte=now, phase2_end_date__gte=now).first()

        # if phase 2 expired globally but the student is given an exception
        if not sem:
            if admission_request and admission_request.phase2_start_date and admission_request.phase2_end_date and \
                    admission_request.phase2_start_date <= now <= admission_request.phase2_end_date:
                sem = admission_request.semester

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
        # was OperationalError and happened when db doesn't exist yet but later changed it to general
        # except to catch an weird exceptions like ProgrammingError
        except:
            return [('--', '--')]


# TODO: combine the two below models into one and add order and note (optional)
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
        ordering = ('status_message_code',)

    @property
    def registration_status_message(self):
        lang = translation.get_language()
        if lang == "ar":
            return self.status_message_ar
        else:
            return self.status_message_en

    def __str__(self):
        try:
            if self.status.status_code != self.status_message_code:
                return '%s (%s)' % (self.status.status_code, self.status_message_code)
            else:
                return self.status_message_code
        except:
            return self.status_message_code

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
        except:
            return

    @staticmethod
    def get_status_transfer():
        try:
            return RegistrationStatus.objects.get(status_code='PARTIALLY-ADMITTED').status_messages. \
                get(status_message_code='TRANSFER')
        except:
            return

    @staticmethod
    def get_status_applied_non_saudi():
        try:
            return RegistrationStatus.objects.get(status_code='APPLIED').status_messages. \
                get(status_message_code='NON-SAUDI')
        except:
            return

    @staticmethod
    def get_status_old_high_school():
        try:
            return RegistrationStatus.objects.get(status_code='REJECTED').status_messages. \
                get(status_message_code='OLD-HS')
        except:
            return

    @staticmethod
    def get_status_girls():
        try:
            return RegistrationStatus.objects.get(status_code='REJECTED').status_messages. \
                get(status_message_code='GIRLS')
        except:
            return

    @staticmethod
    def get_status_withdrawn():
        try:
            return RegistrationStatus.objects.get(status_code='WITHDRAWN').status_messages.first()
        except:
            return

    @staticmethod
    def get_status_partially_admitted():
        try:
            return RegistrationStatusMessage.objects.get(status_message_code='PARTIALLY-ADMITTED')
        except:
            return

    @staticmethod
    def get_status_partially_admitted_non_saudi():
        try:
            return RegistrationStatusMessage.objects.get(status_message_code='PARTIALLY-ADMITTED-NON-SAUDI')
        except:
            return

    @staticmethod
    def get_status_partially_admitted_transfer():
        try:
            return RegistrationStatusMessage.objects.get(status_message_code='PARTIALLY-ADMITTED-TRANSFER')
        except:
            return

    @staticmethod
    def get_status_admitted():
        try:
            return RegistrationStatus.objects.get(status_code='ADMITTED') \
                .status_messages.get(status_message_code='ADMITTED')
        except:
            return

    @staticmethod
    def get_status_admitted_non_saudi():
        try:
            return RegistrationStatus.objects.get(status_code='ADMITTED') \
                .status_messages.get(status_message_code='ADMITTED-N')
        except:
            return

    @staticmethod
    def get_status_admitted_transfer_final():
        try:
            return RegistrationStatus.objects.get(status_code='ADMITTED') \
                .status_messages.get(status_message_code='ADMITTED-FINAL-T')
        except:
            return

    @staticmethod
    def get_status_admitted_final():
        try:
            return RegistrationStatus.objects.get(status_code='ADMITTED') \
                .status_messages.get(status_message_code='ADMITTED-FINAL')
        except:
            return

    @staticmethod
    def get_status_admitted_final_non_saudi():
        try:
            return RegistrationStatus.objects.get(status_code='ADMITTED') \
                .status_messages.get(status_message_code='ADMITTED-FINAL-N')
        except:
            return

    @staticmethod
    def get_status_duplicate():
        try:
            return RegistrationStatus.objects.get(status_code='SUSPENDED') \
                .status_messages.get(status_message_code='DUPLICATE')
        except:
            return

    @staticmethod
    def get_status_confirmed():
        try:
            return RegistrationStatus.objects.get(status_code='PARTIALLY-ADMITTED') \
                .status_messages.get(status_message_code='CONFIRMED')
        except:
            return

    @staticmethod
    def get_status_confirmed_non_saudi():
        try:
            return RegistrationStatus.objects.get(status_code='PARTIALLY-ADMITTED') \
                .status_messages.get(status_message_code='CONFIRMED-N')
        except:
            return

    @staticmethod
    def get_status_confirmed_transfer():
        try:
            return RegistrationStatus.objects.get(status_code='PARTIALLY-ADMITTED') \
                .status_messages.get(status_message_code='CONFIRMED-T')
        except:
            return


class GraduationYear(models.Model):
    class GraduationYearTypes:
        CURRENT_YEAR = 'CURRENT-YEAR'
        LAST_YEAR = 'LAST-YEAR'
        OLD_HS = 'OLD-HS'

        @classmethod
        def choices(cls):
            return (
                (cls.CURRENT_YEAR, _('Current high school graduation year')),
                (cls.LAST_YEAR, _('Previous high school graduation year')),
                (cls.OLD_HS, _('Old High school graduation year')),
            )

    graduation_year_en = models.CharField(max_length=50, verbose_name=_('Graduation Year (English)'))
    graduation_year_ar = models.CharField(max_length=50, verbose_name=_('Graduation Year (Arabic)'))
    description = models.CharField(max_length=200, verbose_name=_('Description'))
    type = models.CharField(max_length=20, verbose_name=_('Type'), choices=GraduationYearTypes.choices(),
                            null=True, blank=False, default=GraduationYearTypes.OLD_HS)
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
        except:  # was OperationalError and happened when db doesn't exist yet but later changed it to general except to catch any weird exceptions like ProgrammingError
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


class VerificationIssues(models.Model):
    class RelatedFields:
        PERSONAL_PICTURE = 'personal_picture'
        HIGH_SCHOOL_CERTIFICATE = 'high_school_certificate'
        MOTHER_GOV_ID_FILE = 'mother_gov_id_file'

        @classmethod
        def choices(cls):
            return (
                (cls.PERSONAL_PICTURE, _('Personal Picture')),
                (cls.HIGH_SCHOOL_CERTIFICATE, _('High School Certificate')),
                (cls.MOTHER_GOV_ID_FILE, _('Mother Government ID')),
            )

    related_field = models.CharField(_('Related Field'), max_length=50, null=True, blank=False,
                                     db_index=True, choices=RelatedFields.choices())
    verification_issue_ar = models.CharField(_('Verification Issue (AR)'), max_length=200, null=True, blank=False)
    verification_issue_en = models.CharField(_('Verification Issue (EN)'), max_length=200, null=True, blank=False)
    show = models.BooleanField(verbose_name=_('Show'), default=True)
    display_order = models.PositiveSmallIntegerField(null=True, verbose_name=_('Display Order'))

    class Meta:
        verbose_name_plural = _('Verification Issues')
        ordering = ['related_field', '-display_order']

    @property
    def verification_issue(self):
        lang = translation.get_language()
        if lang == "ar":
            return self.verification_issue_ar
        else:
            return self.verification_issue_en

    def __str__(self):
        return self.verification_issue

    @staticmethod
    def issues_choices(add_dashes=True):
        try:
            choices = VerificationIssues.objects.filter(show=True)

            ch = [(o.lookup_value, o.pk) for o in choices]
            if add_dashes:
                ch.insert(0, ('', '---------'))

            return ch
        # was OperationalError and happened when db doesn't exist yet but later changed it to general except to catch
        # any weird exceptions like ProgrammingError
        except:
            return [('--', '--')]
