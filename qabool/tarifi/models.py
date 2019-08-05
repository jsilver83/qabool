from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from undergraduate_admission.models import RegistrationStatus, AdmissionSemester, TarifiReceptionDate
from undergraduate_admission.utils import format_date_time, format_date, format_time
from .views import allowed_statuses_for_tarifi_week

User = settings.AUTH_USER_MODEL


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
        verbose_name=_('Semester'),
    )
    slot_start_date = models.DateTimeField(null=True, blank=False, verbose_name=_('Start Date'))
    slot_end_date = models.DateTimeField(null=True, blank=False, verbose_name=_('End Date'))
    location_ar = models.CharField(max_length=600, null=True, blank=False, verbose_name=_('Location (Arabic)'))
    location_en = models.CharField(max_length=600, null=True, blank=False, verbose_name=_('Location (English)'))
    slots = models.PositiveSmallIntegerField(null=True, blank=False, default=300, verbose_name=_('Slots'))
    type = models.CharField(
        _('Slot Type'),
        max_length=30,
        null=True,
        blank=False,
        choices=TarifiActivitySlotTypes.choices(),
    )
    attender = models.ForeignKey(
        User,
        verbose_name=_('Attender'),
        null=True,
        blank=True,
        related_name='assigned_slots',
        on_delete=models.SET_NULL,
    )
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

        return _('%(slot_type)s (%(location)s) %(start_date)s') % {
            'slot_type': self.get_type_display(),
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
        if self.type == TarifiActivitySlot.TarifiActivitySlotTypes.PREPARATION_COURSE:
            return self.slots - TarifiData.objects.filter(
                preparation_course_slot=self.pk,
                admission_request__status_message__in=allowed_statuses_for_tarifi_week).count()
        elif self.type == TarifiActivitySlot.TarifiActivitySlotTypes.ENGLISH_PLACEMENT_TEST:
            return self.slots - TarifiData.objects.filter(
                english_placement_test_slot=self.pk,
                admission_request__status_message__in=allowed_statuses_for_tarifi_week).count()
        elif self.type == TarifiActivitySlot.TarifiActivitySlotTypes.ENGLISH_SPEAKING_TEST:
            return self.slots - TarifiData.objects.filter(
                english_speaking_test_slot=self.pk,
                admission_request__status_message__in=allowed_statuses_for_tarifi_week).count()

    @property
    def slot_attendance_start_date(self):
        return self.slot_start_date - timezone.timedelta(minutes=10)

    @property
    def slot_attendance_end_date(self):
        return self.slot_start_date + timezone.timedelta(minutes=30)


class TarifiData(models.Model):
    admission_request = models.OneToOneField(
        'undergraduate_admission.AdmissionRequest',
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='tarifi_data',
    )

    desk_no = models.CharField(_('Desk No'), null=True, blank=True, max_length=100)
    received_by = models.ForeignKey(
        User,
        verbose_name=_('Received By'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students_received',
    )

    preparation_course_slot = models.ForeignKey(
        'TarifiActivitySlot',
        verbose_name=_('Preparation Course Slot'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students_in_course_slot',
        limit_choices_to={'type': TarifiActivitySlot.TarifiActivitySlotTypes.PREPARATION_COURSE},
    )
    preparation_course_attendance = models.DateTimeField(
        _('Preparation Course Attendance Date'),
        null=True,
        blank=True,
    )
    preparation_course_attended_by = models.ForeignKey(
        User,
        verbose_name=_('Preparation Course Attended By'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attended_students',
        limit_choices_to={'is_staff': True}
    )

    english_placement_test_slot = models.ForeignKey(
        'TarifiActivitySlot',
        verbose_name=_('English Placement Test Slot'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students_in_placement_slot',
        limit_choices_to={'type': TarifiActivitySlot.TarifiActivitySlotTypes.ENGLISH_PLACEMENT_TEST},
    )

    english_speaking_test_slot = models.ForeignKey(
        'TarifiActivitySlot',
        verbose_name=_('English Speaking Test Slot'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students_in_speaking_slot',
        limit_choices_to={'type': TarifiActivitySlot.TarifiActivitySlotTypes.ENGLISH_SPEAKING_TEST},
    )
    english_speaking_test_start_time = models.DateTimeField(
        _('English Speaking Test Time'),
        null=True,
        blank=True,
    )

    english_placement_test_score = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name=_('English Placement Test Score'),
        validators=[MinValueValidator(1),
                    MaxValueValidator(100)],
    )
    english_speaking_test_score = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name=_('English Speaking Test Score'),
        validators=[MinValueValidator(1),
                    MaxValueValidator(100)],
    )
    english_level = models.CharField(max_length=20, null=True, blank=True, verbose_name=_('English Level'))

    created_on = models.DateTimeField(null=True, blank=True, auto_now_add=True, verbose_name=_('Created On'), )
    updated_on = models.DateTimeField(null=True, blank=True, auto_now=True, verbose_name=_('Updated On'), )

    def __str__(self):
        return str(self.admission_request)

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

    def receive(self, receiving_user, use_current_timing=False, reschedule=False):
        if self.received_by is None:
            self.received_by = receiving_user

        if reschedule:
            self.assign_tarifi_activities(use_current_timing=True, reschedule=True)
        else:
            self.assign_tarifi_activities(use_current_timing, reschedule=False)

    def assign_tarifi_activities(self, use_current_timing=False, reschedule=False):
        if use_current_timing:
            reception_date = timezone.now() + timezone.timedelta(minutes=30)
        else:
            try:
                reception_date = self.admission_request.tarifi_week_attendance_date.slot_end_date
            except:
                return

        if reschedule or self.preparation_course_slot is None:
            available_course_slots = TarifiActivitySlot.objects.filter(
                type=TarifiActivitySlot.TarifiActivitySlotTypes.PREPARATION_COURSE,
                show=True,
                slot_start_date__gt=reception_date,
                semester=self.admission_request.semester,
            )
            for course_slot in available_course_slots:
                if course_slot.remaining_slots > 0:
                    self.preparation_course_slot = course_slot
                    break

        if reschedule or self.english_placement_test_slot is None:
            if self.preparation_course_slot:
                acceptable_written_start_date = self.preparation_course_slot.slot_end_date \
                                                + timezone.timedelta(minutes=30)
                available_written_slots = TarifiActivitySlot.objects.filter(
                    type=TarifiActivitySlot.TarifiActivitySlotTypes.ENGLISH_PLACEMENT_TEST,
                    show=True,
                    slot_start_date__gt=acceptable_written_start_date,
                    semester=self.admission_request.semester,
                )

                for written_slot in available_written_slots:
                    if written_slot.remaining_slots > 0:
                        self.english_placement_test_slot = written_slot
                        break

                if reschedule or self.english_speaking_test_slot is None:
                    if self.english_placement_test_slot:
                        acceptable_oral_start_date = self.english_placement_test_slot.slot_end_date \
                                                     + timezone.timedelta(minutes=30)
                        available_oral_slots = TarifiActivitySlot.objects.filter(
                            type=TarifiActivitySlot.TarifiActivitySlotTypes.ENGLISH_SPEAKING_TEST,
                            show=True,
                            slot_start_date__gt=acceptable_oral_start_date,
                            location_en=self.english_placement_test_slot.location_en,
                            semester=self.admission_request.semester,
                        )
                        for oral_slot in available_oral_slots:
                            if oral_slot.remaining_slots > 0:
                                self.english_speaking_test_slot = oral_slot
                                time_offset = (timezone.localtime(oral_slot.slot_end_date)
                                               - timezone.localtime(
                                            oral_slot.slot_start_date)).seconds / oral_slot.slots \
                                              * (oral_slot.slots - oral_slot.remaining_slots)
                                self.english_speaking_test_start_time = timezone.localtime(oral_slot.slot_start_date) \
                                                                        + timezone.timedelta(seconds=time_offset)
                                break

        self.save()

    @staticmethod
    def distribute_admission_requests_in_tarifi_slots(admission_semester, statuses=None,
                                                      use_current_timing=False, send_sms=False):
        admission_requests = admission_semester.applicants.all()
        if statuses:
            admission_requests = admission_requests.filter(status_message__in=statuses)
        else:
            admission_requests = admission_requests.filter(status_message__in=allowed_statuses_for_tarifi_week)

        reception_dates = TarifiReceptionDate.objects.filter(semester=admission_semester)

        for reception_date in reception_dates:
            reception_date_admission_requests = admission_requests.filter(tarifi_week_attendance_date=reception_date)
            counter = 1

            for admission_request in reception_date_admission_requests:
                tarifi_data, created = TarifiData.objects.get_or_create(admission_request=admission_request)

                # only assign a reception desk if the student doesnt have it assigned already; otherwise, keep it as is
                if created or tarifi_data.desk_no is None:
                    tarifi_data.desk_no = counter
                    print(counter)
                    tarifi_data.save()
                    counter += 1
                    if counter > settings.TARIFI_NO_OF_DESKS_IN_RECEPTION:
                        counter = 1

                tarifi_data.assign_tarifi_activities(use_current_timing=False)

                if send_sms:
                    # TODO: implement
                    pass


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
