import django_filters as filters
from django.utils.translation import ugettext_lazy as _

from undergraduate_admission.models import AdmissionSemester, Lookup, AdmissionRequest
from .models import HousingUser, RoommateRequest


class HousingUserFilter(filters.FilterSet):
    high_school_city = filters.ChoiceFilter(choices=AdmissionRequest.get_distinct_high_school_city(add_dashes=False),
                                            required=False, field_name='user__high_school_city',
                                            label=_('School City'))
    high_school_name = filters.CharFilter(label=_('School Name'), field_name='user__high_school_name',
                                          lookup_expr='icontains')
    sleeping = filters.ChoiceFilter(choices=Lookup.get_lookup_choices(Lookup.LookupTypes.HOUSING_PREF_SLEEPIN,
                                                                      add_dashes=False), required=False)
    light = filters.ChoiceFilter(choices=Lookup.get_lookup_choices(Lookup.LookupTypes.HOUSING_PREF_LIGHT,
                                                                   add_dashes=False), required=False)
    room_temperature = filters.ChoiceFilter(choices=Lookup.get_lookup_choices(Lookup.LookupTypes.HOUSING_PREF_AC,
                                                                              add_dashes=False), required=False)
    visits = filters.ChoiceFilter(choices=Lookup.get_lookup_choices(Lookup.LookupTypes.HOUSING_PREF_VISITS,
                                                                    add_dashes=False), required=False)

    class Meta:
        model = HousingUser
        fields = ['high_school_city', 'high_school_name', 'sleeping', 'light', 'room_temperature', 'visits']

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        super().__init__(data, queryset, request=request, prefix=prefix)

    @property
    def qs(self):
        from .views import allowed_statuses_for_housing
        return super().qs \
            .filter(user__status_message__in=allowed_statuses_for_housing,
                    user__semester=AdmissionSemester.get_phase4_active_semester(),
                    searchable=True,
                    user__eligible_for_housing=True) \
            .exclude(user__pk__in=RoommateRequest.objects.
                     filter(status=RoommateRequest.RequestStatuses.ACCEPTED)
                     .values_list('requesting_user__pk', flat=True)) \
            .exclude(user__pk__in=RoommateRequest.objects.
                     filter(status=RoommateRequest.RequestStatuses.ACCEPTED)
                     .values_list('requested_user__pk', flat=True))
