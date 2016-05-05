from django.conf.urls import url, include
from django.contrib.auth.views import login, logout

from . import views

urlpatterns = [
    url(
        r'^login/$',
        login,
        name='login',
        kwargs={'template_name': 'undergraduate_admission/login.html'}
    ),
    url(
        r'^logout/$',
        logout,
        name='logout',
        kwargs={'next_page': '/'}
    ),
    url(r'^register/$', views.RegisterView.as_view(), name='register'),
    url(r'^$', views.IndexView, name='index'),
]
