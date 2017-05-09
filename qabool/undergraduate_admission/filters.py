import django_filters
from .models import User


class UserListFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = ['semester', 'username', 'nationality', 'gender', 'high_school_graduation_year', ]
        order_by = ['username']
