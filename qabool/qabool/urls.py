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

    url(r'^files/(?P<filetype>[\w\-]+)/(?P<pk>\d+)/$',
        phase2_views.UserFileView.as_view(),
        name='download_user_file'),

    url(r'^uploaded_docs/(?P<filename>.*)/$',
        phase2_views.media_view,
        name='user_file'),
)
