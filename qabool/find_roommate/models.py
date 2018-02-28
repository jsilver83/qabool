from django.db import models
from django.db.models import Q

from django.utils.translation import ugettext_lazy as _

from undergraduate_admission.models import User


class HousingUser(models.Model):
    user = models.OneToOneField(
        'undergraduate_admission.User',
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='housing_user',
    )
    facebook = models.URLField(null=True, blank=True, max_length=150, verbose_name=_('Facebook'))
    twitter = models.URLField(null=True, blank=True, max_length=150, verbose_name=_('Twitter'))
    sleeping = models.CharField(null=True, blank=True, max_length=150, verbose_name=_('Sleeping'))
    light = models.CharField(null=True, blank=True, max_length=150, verbose_name=_('Light'))
    room_temperature = models.CharField(null=True, blank=True, max_length=150,
                                        verbose_name=_('Room Temperature'))
    visits = models.CharField(null=True, blank=True, max_length=150, verbose_name=_('Visits'))
    interests_and_hobbies = models.TextField(null=True, blank=True, max_length=1000,
                                             verbose_name=_('Interests And Hobbies'))
    searchable = models.NullBooleanField(verbose_name=_('Searchable'))

    def __str__(self):
        return str(self.user)


class RoommateRequest(models.Model):
    class RequestStatuses:
        PENDING = 'P'
        ACCEPTED = 'A'
        REJECTED = 'R'
        REQUESTING_STUDENT_WITHDRAWN = 'W1'
        REQUESTED_STUDENT_WITHDRAWN = 'W2'
        EXPIRED = 'E'
        CANCELLED = 'C'

        @classmethod
        def choices(cls):
            return (
                (cls.PENDING, _('Pending')),
                (cls.ACCEPTED, _('Accepted')),
                (cls.REJECTED, _('Rejected')),
                (cls.REQUESTING_STUDENT_WITHDRAWN, _('Requesting Student Withdrawn')),
                (cls.REQUESTED_STUDENT_WITHDRAWN, _('Requested Student Withdrawn')),
                (cls.EXPIRED, _('Expired')),
                (cls.CANCELLED, _('Cancelled By Requester')),
            )

    requesting_user = models.ForeignKey(
        'undergraduate_admission.User',
        on_delete=models.CASCADE,
        related_name='roommate_request_sent',
        null=True,
        blank=False,
    )
    requested_user = models.ForeignKey(
        'undergraduate_admission.User',
        on_delete=models.SET_NULL,
        related_name='roommate_request_received',
        null=True,
        blank=False,
    )
    status = models.CharField(
        null=True,
        blank=True,
        max_length=10,
        choices=RequestStatuses.choices(),
        verbose_name=_('Status'),
        default=RequestStatuses.PENDING,
    )
    assigned_room = models.ForeignKey(
        'Room',
        on_delete=models.SET_NULL,
        related_name='residing',
        null=True,
        blank=True,
        verbose_name=_('Assigned Room'),
    )
    request_date = models.DateTimeField(null=True, blank=False, auto_now_add=True, verbose_name=_('Request Date'), )
    updated_on = models.DateTimeField(null=True, blank=False, auto_now=True, verbose_name=_('Updated On'), )

    def requesting_user__kfupm_id(self):
        return self.requesting_user.kfupm_id

    def requested_user__kfupm_id(self):
        return self.requested_user.kfupm_id

    def __str__(self):
        return '%s & %s' % (self.requesting_user, self.requested_user)


class Room(models.Model):
    building = models.CharField(null=True, blank=False, max_length=20, verbose_name=_('Building'), )
    room = models.CharField(null=True, blank=False, max_length=20, verbose_name=_('Room'), )
    available = models.BooleanField(default=True, verbose_name=_('Available'), )

    class Meta:
        unique_together = ['building', 'room']

    def __str__(self):
        return '%s - %s' % (self.building, self.room)

    def residents(self):
        return RoommateRequest.objects.filter(status=RoommateRequest.RequestStatuses.ACCEPTED,
                                              assigned_room=self).first()

    @staticmethod
    def get_next_available_room():
        return Room.objects.filter(available=True). \
            exclude(pk__in=RoommateRequest.objects.filter(status=RoommateRequest.RequestStatuses.ACCEPTED)
                    .exclude(assigned_room__isnull=True)
                    .values_list('assigned_room', flat=True)).order_by('?').first()

    @staticmethod
    def get_assigned_room(user):
        request = RoommateRequest.objects.filter(Q(requesting_user=user) | Q(requested_user=user),
                                                 status=RoommateRequest.RequestStatuses.ACCEPTED).first()
        if request:
            return request.assigned_room
