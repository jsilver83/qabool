from django.conf.urls import url
from django.contrib.auth.views import login, logout

from . import views

urlpatterns = [
    url(
        r'^login/$',
        # login,
        views.index,
        name='login',
        # kwargs={'template_name': 'undergraduate_admission/login.html'}
    ),
    url(
        r'^logout/$',
        logout,
        name='logout',
        kwargs={'next_page': '/'}
    ),
    url(r'^register/$', views.RegisterView.as_view(), name='register'),
    url(r'^studentarea/$', views.student_area, name='student_area'),
    url(r'^registrationsuccess/$', views.registration_success, name='registration_success'),
    url(r'^initialagreement/$', views.initial_agreement, name='initial_agreement'),
    url(r'^forgotpassword/$', views.forgot_password, name='forgot_password'),
    url(r'^$', views.index, name='index'),
]
