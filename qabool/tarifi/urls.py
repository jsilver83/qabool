from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^simulation/$', TarifiSimulation.as_view(), name='tarifi_simulation'),
    url(r'^student/(?P<pk>\d+)/$', StudentPrintPage.as_view(), name='student_print_page'),
    url(r'^attendance/$', CourseAttendance.as_view(), name='preparation_course_attendance'),
    url(r'', TarifiLandingPage.as_view(), name='tarifi_landing_page'),
]

