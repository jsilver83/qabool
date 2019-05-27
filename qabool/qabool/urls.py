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
from django.conf.urls import include
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.auth import views
from django.urls import path

from . import settings
from django.conf.urls.static import static

from undergraduate_admission.views import phase2_views

urlpatterns = i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('undergraduate_admission.urls')),
    path('roommate/', include('find_roommate.urls')),
    # path('admin/tarifi/', include('tarifi.urls')),
    path('logout/', views.LogoutView.as_view(), {'template_name': 'logout.html'}, name='logout'),
)

urlpatterns += [
    path('captcha/', include(captcha.urls)),

    path('uploaded_docs/<slug:filetype>/<str:semester_name>/<str:gov_id>.<str:extension>/',
         phase2_views.UserFileRouterView.as_view(),
         name='user_file'),

    path('files/<slug:filetype>/<int:pk>/',
         phase2_views.UserFileView.as_view(),
         name='download_user_file'),

    path('admin_files/<slug:filetype>/<int:pk>/',
         phase2_views.UserFileView.as_view(),
         name='download_user_file_admin'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)