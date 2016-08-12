from django.db import models

from django.utils.translation import ugettext_lazy as _

from undergraduate_admission.models import User


class HousingUser(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='housing_user',
    )
    facebook = models.URLField(null=True, blank=True, max_length=150, verbose_name=_('Facebook'))
    twitter = models.URLField(null=True, blank=True, max_length=150, verbose_name=_('Twitter'))
    sleeping = models.CharField(null=True, blank=False, max_length=150, verbose_name=_('Sleeping'))
    light = models.CharField(null=True, blank=False, max_length=150, verbose_name=_('Light'))
    room_temperature = models.CharField(null=True, blank=False, max_length=150,
                                        verbose_name=_('Room Temperature'))
    visits = models.CharField(null=True, blank=False, max_length=150, verbose_name=_('Visits'))
    interests_and_hobbies = models.TextField(null=True, blank=True, max_length=1000,
                                             verbose_name=_('Interests And Hobbies'))
    searchable = models.NullBooleanField(verbose_name=_('Searchable'))

    def __str__(self):
        return str(self.user)
