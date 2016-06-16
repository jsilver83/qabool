"""qabool URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
import captcha.urls
from django.conf.urls import url, include, patterns
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin

import undergraduate_admission.urls
from undergraduate_admission.views import phase2_views

urlpatterns = i18n_patterns(
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += i18n_patterns(
    url(r'', include(undergraduate_admission.urls))
)

urlpatterns += patterns('',
                        url(r'^captcha/', include(captcha.urls)),

                        url(r'^files/birth-certificate/(?P<pk>\d+)/$',
                            phase2_views.BirthCertificate.as_view(),
                            name='birth_certificate'),

                        url(r'^files/high-school-certificate/(?P<pk>\d+)/$',
                            phase2_views.HighSchoolCertificate.as_view(),
                            name='high_school_certificate'),

                        url(r'^files/gov-id-file/(?P<pk>\d+)/$',
                            phase2_views.GovernmentIDFile.as_view(),
                            name='gov_id_file'),

                        url(r'^files/mother-gov-id-file/(?P<pk>\d+)/$',
                            phase2_views.MotherGovernmentIDFile.as_view(),
                            name='mother_gov_id_file'),

                        url(r'^files/passport-file/(?P<pk>\d+)/$',
                            phase2_views.PassportFile.as_view(),
                            name='passport_file'),

                        url(r'^files/personal-picture/(?P<pk>\d+)/$',
                            phase2_views.PersonalPicture.as_view(),
                            name='personal_picture'),

                        url(r'^files/courses-certificate/(?P<pk>\d+)/$',
                            phase2_views.CoursesCertificate.as_view(),
                            name='courses_certificate'),
                        )
