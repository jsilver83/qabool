from django.conf.urls import url

from .views import housing_info_update, housing_search, PostList
from .models import User

urlpatterns = [
    url(r'^findroommate/$', housing_info_update, name='housing_info_update'),
    # url(r'^housingsearch/$', PostList.as_view(), name='housing_search'),
    url(r'^housingsearch/$', housing_search, name='housing_search'),
]
