from django.conf.urls import url

from .views import *
from .models import User

urlpatterns = [
    url(r'^findroommate/$', housing_info_update, name='housing_info_update'),
    url(r'^housingsearch/$', housing_search, name='housing_search'),
    url(r'^housingletter2/$', housing_letter2, name='housing_letter2'),
    url(r'^housingletter1/$', housing_letter1, name='housing_letter1'),
]
