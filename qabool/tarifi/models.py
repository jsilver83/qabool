from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from undergraduate_admission.models import RegistrationStatusMessage, User, AdmissionSemester


class TarifiUser(models.Model):
    user = models.OneToOneField(
        'undergraduate_admission.User',
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='tarifi_user',
    )
    preparation_course_attendance_date = models.ForeignKey('TarifiActivitySlot',
                                                           verbose_name=_('Preparation Course Attendance Date'),
                                                           on_delete=models.SET_NULL,
                                                           null=True,
                                                           blank=True,
                                                           related_name='students_in_course_slot',
                                                           limit_choices_to={'type': 'PREPARATION_COURSE'})
    english_placement_test_date = models.ForeignKey('TarifiActivitySlot',
                                                    verbose_name=_('English Placement Test Date'),
                                                    on_delete=models.SET_NULL,
                                                    null=True,
                                                    blank=True,
                                                    related_name='students_in_placement_slot',
                                                    limit_choices_to={'type': 'ENGLISH_PLACEMENT_TEST'})
    english_speaking_test_date = models.ForeignKey('TarifiActivitySlot',
                                                   verbose_name=_('English Speaking Test Date'),
                                                   on_delete=models.SET_NULL,
                                                   null=True,
                                                   blank=True,
                                                   related_name='students_in_speaking_slot',
                                                   limit_choices_to={'type': 'ENGLISH_SPEAKING_TEST'})
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

    def __str__(self):
        return str(self.user)


class TarifiActivitySlot(models.Model):
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
    type = models.CharField(max_length=30, null=True, blank=False, verbose_name=_('Slot Type'),
                            choices=[
                                ('PREPARATION_COURSE', _('Preparation Course Attendance Date')),
                                ('ENGLISH_PLACEMENT_TEST', _('English Placement Test Date')),
                                ('ENGLISH_SPEAKING_TEST', _('English Speaking Test Date'))]
                            )
    description = models.CharField(max_length=600, null=True, blank=True, verbose_name=_('Description'))
    show = models.BooleanField(verbose_name=_('Show'), default=True)
    display_order = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=_('Display Order'))

    class Meta:
        verbose_name_plural = _('Tarifi: Preparation Activity Slots')

    # def __str__(self):
    #     if translation.get_language() == "ar":
    #         location = self.location_ar
    #     else:
    #         location = self.location_en
    #
    #     if self.type == 'PREPARATION_COURSE':
    #         slot_type = _('Preparation Course Attendance')
    #     elif self.type == 'ENGLISH_PLACEMENT_TEST':
    #         slot_type = _('English Placement Test')
    #     elif self.type == 'ENGLISH_SPEAKING_TEST':
    #         slot_type = _('English Speaking Test')
    #     else:
    #         slot_type = 'N/A'
    #
    #     return _('%(slot_type)s (%(location)s) - %(start_date)s to %(end_date)s') % {
    #         'slot_type': slot_type,
    #         'location': location,
    #         'start_date': self.slot_start_date,
    #         'end_date': self.slot_end_date,
    #     }

    @property
    def remaining_slots(self):
        if self.type == 'PREPARATION_COURSE':
            return self.slots - TarifiUser.objects.filter(
                preparation_course_attendance_date=self.pk,
                user__status_message=RegistrationStatusMessage.get_status_admitted()).count()
        elif self.type == 'ENGLISH_PLACEMENT_TEST':
            return self.slots - TarifiUser.objects.filter(
                english_placement_test_date=self.pk,
                user__status_message=RegistrationStatusMessage.get_status_admitted()).count()
        elif self.type == 'ENGLISH_SPEAKING_TEST':
            return self.slots - TarifiUser.objects.filter(
                english_speaking_test_date=self.pk,
                user__status_message=RegistrationStatusMessage.get_status_admitted()).count()

    # TODO: Implement next available slot logic
    @staticmethod
    def get_next_preparation_course_available_slot(student):
        pass

    @staticmethod
    def get_next_placement_test_available_slot(student):
        pass

    @staticmethod
    def get_next_speaking_test_available_slot(student):
        pass
