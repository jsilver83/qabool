from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class FindRoommateConfig(AppConfig):
    name = 'find_roommate'
    verbose_name = _('Find Roommate App')

    # def ready(self):
    #     import find_roommate.signals