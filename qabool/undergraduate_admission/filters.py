import django_filters
from .models import User


class UserListFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = ['semester', 'username', 'nationality', 'gender', 'status_message', ]
        order_by = ['username']
