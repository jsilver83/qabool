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
from django_downloadview import ObjectDownloadView

import undergraduate_admission.urls
from qabool import settings
from undergraduate_admission.models import User

# urlpatterns = [
#     url(r'^admin/', admin.site.urls),
#     # url(r'^i18n/', include('django.conf.urls.i18n')),
# ]
from undergraduate_admission.views import phase2_views

urlpatterns = i18n_patterns(
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += i18n_patterns(
    url(r'', include(undergraduate_admission.urls))
)

urlpatterns += patterns('',
                        url(r'^captcha/', include(captcha.urls)),

                        url(r'^file-birth_certificate/(?P<pk>\d+)/$',
                            ObjectDownloadView.as_view(
                                model=User,
                                file_field='birth_certificate'),
                            name='birth_certificate'),

                        url(r'^file-high_school_certificate/(?P<pk>\d+)/$',
                            ObjectDownloadView.as_view(
                                model=User,
                                file_field='high_school_certificate'),
                            name='high_school_certificate'),

                        url(r'^file-government_id_file/(?P<pk>\d+)/$',
                            ObjectDownloadView.as_view(
                                model=User,
                                file_field='government_id_file'),
                            name='government_id_file'),

                        url(r'^file-mother_gov_id_file/(?P<pk>\d+)/$',
                            ObjectDownloadView.as_view(
                                model=User,
                                file_field='mother_gov_id_file'),
                            name='mother_gov_id_file'),

                        url(r'^file-passport_file/(?P<pk>\d+)/$',
                            ObjectDownloadView.as_view(
                                model=User,
                                file_field='passport_file'),
                            name='passport_file'),

                        url(r'^file-personal_picture/(?P<pk>\d+)/$',
                            ObjectDownloadView.as_view(
                                model=User,
                                file_field='personal_picture'),
                            name='personal_picture'),

                        url(r'^file-courses_certificate/(?P<pk>\d+)/$',
                            ObjectDownloadView.as_view(
                                model=User,
                                file_field='courses_certificate'),
                            name='courses_certificate'),

                        # url(r'^%s/(?P<filename>.*)/$'%settings.MEDIA_URL[1:-1],
                        #     phase2_views.media_view,
                        #     name='media_file'),
                        )

# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)