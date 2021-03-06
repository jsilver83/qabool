from django.urls import path

from .views import *

app_name = 'tarifi'

urlpatterns = [
    path('simulation/', TarifiSimulation.as_view(), name='tarifi_simulation'),
    path('student/<int:pk>/', StudentPrintPage.as_view(), name='student_print_page'),
    path('attendance/', CourseAttendance.as_view(), name='preparation_course_attendance'),
    path('reception-landing/', ReceptionLanding.as_view(), name='reception_landing'),
    path('reception/', ReceptionAttendance.as_view(), name='reception'),
]
