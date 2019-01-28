import django_filters
from .models import AdmissionRequest


class AdmissionRequestListFilter(django_filters.FilterSet):
    class Meta:
        model = AdmissionRequest
        fields = ['semester', 'user__username', 'nationality', 'gender', 'status_message', ]
        order_by = ['user__username']
