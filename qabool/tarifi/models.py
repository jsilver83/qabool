from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from undergraduate_admission.models import RegistrationStatusMessage, User, AdmissionSemester
from undergraduate_admission.utils import format_date_time, format_date, format_time


class TarifiUser(models.Model):
    user = models.OneToOneField(
        'undergraduate_admission.User',
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='tarifi_user',
    )
    received_by = models.ForeignKey('undergraduate_admission.User',
                                    verbose_name='Received By',
                                    on_delete=models.SET_NULL,
                                    null=True,
                                    blank=True,
                                    related_name='students_received',
                                    limit_choices_to={'is_staff': True})
    preparation_course_slot = models.ForeignKey('TarifiActivitySlot',
                                                verbose_name=_('Preparation Course Slot'),
                                                on_delete=models.SET_NULL,
                                                null=True,
                                                blank=True,
                                                related_name='students_in_course_slot',
                                                limit_choices_to={'type': 'PREPARATION_COURSE'})
    preparation_course_attendance = models.DateTimeField(_('Preparation Course Attendance Date'),
                                                         null=True,
                                                         blank=True, )
    preparation_course_attended_by = models.ForeignKey('undergraduate_admission.User',
                                                       verbose_name='Preparation Course Attended By',
                                                       on_delete=models.SET_NULL,
                                                       null=True,
                                                       blank=True,
                                                       related_name='attended_students',
                                                       limit_choices_to={'is_staff': True})
    english_placement_test_slot = models.ForeignKey('TarifiActivitySlot',
                                                    verbose_name=_('English Placement Test Slot'),
                                                    on_delete=models.SET_NULL,
                                                    null=True,
                                                    blank=True,
                                                    related_name='students_in_placement_slot',
                                                    limit_choices_to={'type': 'ENGLISH_PLACEMENT_TEST'})
    english_speaking_test_slot = models.ForeignKey('TarifiActivitySlot',
                                                   verbose_name=_('English Speaking Test Slot'),
                                                   on_delete=models.SET_NULL,
                                                   null=True,
                                                   blank=True,
                                                   related_name='students_in_speaking_slot',
                                                   limit_choices_to={'type': 'ENGLISH_SPEAKING_TEST'})
    english_speaking_test_start_time = models.DateTimeField(_('English Speaking Test Time'),
                                                            null=True,
                                                            blank=True, )
    english_placement_test_score = models.PositiveSmallIntegerField(null=True,
                                                                    blank=True,
                                                                    verbose_name=_('English Placement Test Score'),
                                                                    validators=[MinValueValidator(1),
                                                                                MaxValueValidator(100)], )
    english_speaking_test_score = models.PositiveSmallIntegerField(null=True,
                                                                   blank=True,
                                                                   verbose_name='English Speaking Test Score',
                                                                   validators=[MinValueValidator(1),
                                                                               MaxValueValidator(100)], )
    english_level = models.CharField(max_length=20, null=True, blank=True, verbose_name='English Level')
    creation_date = models.DateTimeField(null=True, blank=True, auto_now_add=True, verbose_name=_('Reception Date'), )
    updated_on = models.DateTimeField(null=True, blank=True, auto_now=True, verbose_name=_('Updated On'), )

    def __str__(self):
        return str(self.user)

    def get_english_speaking_test_date_time(self):
        try:
            if translation.get_language() == "ar":
                location = self.english_speaking_test_slot.location_ar
            else:
                location = self.english_speaking_test_slot.location_en

            return _('%(slot_type)s (%(location)s) %(start_date)s %(start_time)s') % {
                'slot_type': _('English Speaking Test'),
                'location': location,
                'start_date': format_date(self.english_speaking_test_slot.slot_start_date),
                'start_time': format_time(self.english_speaking_test_start_time)
            }
        except AttributeError:
            return ''
        
    @staticmethod
    def assign_tarifi_activities(tarifi_user, receiving_user):
        if tarifi_user.received_by is None:
            tarifi_user.received_by = receiving_user

        current_date = timezone.now() + timezone.timedelta(minutes=30)

        available_course_slots = TarifiActivitySlot.objects.filter(type='PREPARATION_COURSE',
                                                                   show=True,
                                                                   slot_start_date__gt=current_date)

        course_slot = None
        for course_slot in available_course_slots:
            if course_slot.remaining_slots > 0:
                tarifi_user.preparation_course_slot = course_slot
                break

        if course_slot:
            acceptable_written_start_date = course_slot.slot_end_date \
                                            + timezone.timedelta(minutes=30)
            available_written_slots = TarifiActivitySlot.objects.filter(type='ENGLISH_PLACEMENT_TEST',
                                                                        show=True,
                                                                        slot_start_date__gt=acceptable_written_start_date)

            written_slot = None
            for written_slot in available_written_slots:
                if written_slot.remaining_slots > 0:
                    tarifi_user.english_placement_test_slot = written_slot
                    break

            if written_slot:
                acceptable_oral_start_date = written_slot.slot_end_date \
                                             + timezone.timedelta(minutes=30)
                available_oral_slots = TarifiActivitySlot.objects \
                    .filter(type='ENGLISH_SPEAKING_TEST',
                            show=True,
                            slot_start_date__gt=acceptable_oral_start_date,
                            location_en=written_slot.location_en)
                for oral_slot in available_oral_slots:
                    if oral_slot.remaining_slots > 0:
                        tarifi_user.english_speaking_test_slot = oral_slot
                        time_offset = (timezone.localtime(oral_slot.slot_end_date)
                                       - timezone.localtime(oral_slot.slot_start_date)).seconds / oral_slot.slots \
                                      * (oral_slot.slots - oral_slot.remaining_slots)
                        tarifi_user.english_speaking_test_start_time = timezone.localtime(oral_slot.slot_start_date) \
                                                                       + timezone.timedelta(seconds=time_offset)
                        break

        tarifi_user.save()


class TarifiActivitySlot(models.Model):
    class TarifiActivitySlotTypes:
        PREPARATION_COURSE = 'PREPARATION_COURSE'
        ENGLISH_PLACEMENT_TEST = 'ENGLISH_PLACEMENT_TEST'
        ENGLISH_SPEAKING_TEST = 'ENGLISH_SPEAKING_TEST'

        @classmethod
        def choices(cls):
            return (
                (cls.PREPARATION_COURSE, _('Preparation Course Attendance Date')),
                (cls.ENGLISH_PLACEMENT_TEST, _('English Placement Test Date')),
                (cls.ENGLISH_SPEAKING_TEST, _('English Speaking Test Date')),
            )

    semester = models.ForeignKey(
        'undergraduate_admission.AdmissionSemester',
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        related_name='tarifi_activities_dates',
        verbose_name='Semester',
    )
    slot_start_date = models.DateTimeField(null=True, blank=False, verbose_name=_('Start Date'))
    slot_end_date = models.DateTimeField(null=True, blank=False, verbose_name=_('End Date'))
    location_ar = models.CharField(max_length=600, null=True, blank=False, verbose_name=_('Location (Arabic)'))
    location_en = models.CharField(max_length=600, null=True, blank=False, verbose_name=_('Location (English)'))
    slots = models.PositiveSmallIntegerField(null=True, blank=False, default=300, verbose_name=_('Slots'))
    type = models.CharField(max_length=30, null=True, blank=False,
                            verbose_name=_('Slot Type'),
                            choices=TarifiActivitySlotTypes.choices())
    attender = models.ForeignKey('undergraduate_admission.User',
                                 verbose_name=_('Attender'),
                                 null=True,
                                 blank=True,
                                 related_name='assigned_slots',
                                 limit_choices_to={'is_staff': True})
    description = models.CharField(max_length=600, null=True, blank=True, verbose_name=_('Description'))
    show = models.BooleanField(verbose_name=_('Show'), default=True)
    display_order = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=_('Display Order'))

    class Meta:
        verbose_name_plural = _('Tarifi: Preparation Activity Slots')
        ordering = ['display_order', 'slot_start_date']

    def __str__(self):
        if translation.get_language() == "ar":
            location = self.location_ar
        else:
            location = self.location_en

        if self.type == 'PREPARATION_COURSE':
            slot_type = _('Preparation Course Attendance')
        elif self.type == 'ENGLISH_PLACEMENT_TEST':
            slot_type = _('English Placement Test')
        elif self.type == 'ENGLISH_SPEAKING_TEST':
            slot_type = _('English Speaking Test')
        else:
            slot_type = 'N/A'

        return _('%(slot_type)s (%(location)s) %(start_date)s') % {
            'slot_type': slot_type,
            'location': location,
            'start_date': format_date_time(self.slot_start_date),
            # 'end_date': format_date_time(self.slot_end_date),
        }

    @property
    def location(self):
        if translation.get_language() == "ar":
            return self.location_ar
        else:
            return self.location_en

    @property
    def remaining_slots(self):
        if self.type == 'PREPARATION_COURSE':
            return self.slots - TarifiUser.objects.filter(
                preparation_course_slot=self.pk,
                user__status_message=RegistrationStatusMessage.get_status_admitted_final()).count()
        elif self.type == 'ENGLISH_PLACEMENT_TEST':
            return self.slots - TarifiUser.objects.filter(
                english_placement_test_slot=self.pk,
                user__status_message=RegistrationStatusMessage.get_status_admitted_final()).count()
        elif self.type == 'ENGLISH_SPEAKING_TEST':
            return self.slots - TarifiUser.objects.filter(
                english_speaking_test_slot=self.pk,
                user__status_message=RegistrationStatusMessage.get_status_admitted_final()).count()

    @property
    def slot_attendance_start_date(self):
        return self.slot_start_date - timezone.timedelta(minutes=10)

    @property
    def slot_attendance_end_date(self):
        return self.slot_start_date + timezone.timedelta(minutes=30)


class BoxesForIDRanges(models.Model):
    from_kfupm_id = models.PositiveIntegerField(null=True, blank=False, verbose_name=_('From KFUPM ID'))
    to_kfupm_id = models.PositiveIntegerField(null=True, blank=False, verbose_name=_('To KFUPM ID'))
    box_no = models.CharField(max_length=20, null=True, blank=False, verbose_name=_('Box No'))

    def __str__(self):
        return self.box_no


class StudentIssue(models.Model):
    kfupm_id = models.PositiveIntegerField(null=True, blank=False, verbose_name=_('KFUPM ID'))
    issues = models.CharField(max_length=500, null=True, blank=False, verbose_name=_('Box No'))
    show = models.BooleanField(verbose_name=_('Show'), default=True)

    def __str__(self):
        return self.issues
