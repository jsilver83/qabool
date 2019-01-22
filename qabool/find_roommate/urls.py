from django.urls import path

from .views import *

app_name = 'find_roommate'

urlpatterns = [
    path('accept-request/<int:pk>/', AcceptRequest.as_view(), name='accept_request'),
    path('reject-request/<int:pk>/', RejectRequest.as_view(), name='reject_request'),
    path('expire-request/<int:pk>/', CancelRequest.as_view(), name='cancel_request'),
    path('housing-landing/', HousingLandingPage.as_view(), name='housing_landing_page'),
    path('roommate-request/', NewRoommateRequest.as_view(), name='roommate_request'),
    path('housing-agreement/', HousingAgreement.as_view(), name='housing_agreement'),
    path('find-roommate/', HousingInfoUpdate.as_view(), name='housing_info_update'),
    path('housing-search/', housing_search, name='housing_search'),
    path('housing-letter3/', HousingLetter3.as_view(), name='housing_letter3'),
    path('housing-letter2/', HousingLetter2.as_view(), name='housing_letter2'),
    path('housing-letter1/', HousingLetter1.as_view(), name='housing_letter1'),
]
