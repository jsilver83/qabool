from django.conf.urls import url

from .views import *
from .models import User

urlpatterns = [
    url(r'^acceptrequest/(?P<pk>\d+)/$', AcceptRequest.as_view(), name='accept_request'),
    url(r'^rejectrequest/(?P<pk>\d+)/$', RejectRequest.as_view(), name='reject_request'),
    url(r'^housinglanding/$', HousingLandingPage.as_view(), name='housing_landing_page'),
    url(r'^roommaterequest/$', NewRoommateRequest.as_view(), name='roommate_request'),
    url(r'^housingagreement/$', HousingAgreement.as_view(), name='housing_agreement'),
    url(r'^findroommate/$', housing_info_update, name='housing_info_update'),
    url(r'^housingsearch/$', housing_search, name='housing_search'),
    url(r'^housingletter2/$', housing_letter2, name='housing_letter2'),
    url(r'^housingletter1/$', housing_letter1, name='housing_letter1'),
]
