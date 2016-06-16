from django_downloadview import ObjectDownloadView

from django.conf.urls import url, include
from django.contrib.auth.views import login, logout, password_change, password_change_done

from .views import general_views, phase1_views, phase2_views
from .models import User

urlpatterns = [
    url(
        r'^login/$',
        # login,
        general_views.index,
        name='login',
        # kwargs={'template_name': 'undergraduate_admission/login.html'}
    ),
    url(
        r'^logout/$',
        logout,
        name='logout',
        kwargs={'next_page': '/'}
    ),
    url(
        r'^changepassword/',
        password_change,
        name='change_password',
        kwargs={'template_name': 'undergraduate_admission/change_password.html'},
    ),
    url(
        r'^changepassworddone/',
        password_change_done,
        name='password_change_done',
        kwargs={'template_name': 'undergraduate_admission/change_password.html'},
    ),
    url(r'^withdrawalletter/$', phase2_views.withdrawal_letter, name='withdrawal_letter'),
    url(r'^withdraw/$', phase2_views.withdraw, name='withdraw'),
    url(r'^medicalletter/$', phase2_views.medical_letter, name='medical_letter'),
    url(r'^admissionletter/$', phase2_views.admission_letter, name='admission_letter'),
    url(r'^printdocuments/$', phase2_views.print_documents, name='print_documents'),
    # url(r'^studentagreement5/$', phase2_views.student_agreement_5, name='student_agreement_5'),
    url(r'^studentagreement4/$', phase2_views.student_agreement_4, name='student_agreement_4'),
    url(r'^studentagreement3/$', phase2_views.student_agreement_3, name='student_agreement_3'),
    url(r'^studentagreement2/$', phase2_views.student_agreement_2, name='student_agreement_2'),
    url(r'^studentagreement1/$', phase2_views.student_agreement_1, name='student_agreement_1'),
    url(r'^uploaddocuments/$', phase2_views.upload_documents, name='upload_documents'),
    url(r'^relativecontact/$', phase2_views.relative_contact, name='relative_contact'),
    url(r'^guardiancontact/$', phase2_views.guardian_contact, name='guardian_contact'),
    url(r'^personalinfo/$', phase2_views.personal_info, name='personal_info'),
    url(r'^confirm/$', phase2_views.confirm, name='confirm'),
    url(r'^editinfo/$', phase1_views.edit_info, name='edit_info'),
    url(r'^editcontactinfo/$', general_views.edit_contact_info, name='edit_contact_info'),
    url(r'^register/$', phase1_views.RegisterView.as_view(), name='register'),
    url(r'^studentarea/$', general_views.student_area, name='student_area'),
    url(r'^registrationsuccess/$', phase1_views.registration_success, name='registration_success'),
    url(r'^initialagreement/$', phase1_views.initial_agreement, name='initial_agreement'),
    url(r'^forgotpassword/$', general_views.forgot_password, name='forgot_password'),
    url(r'^$', general_views.index, name='index'),

    url(r'^file-birth/(?P<username>[a-zA-Z0-9_-]+)/$',
        ObjectDownloadView.as_view(
            model=User,
            file_field='birth_certificate'),
        name='birth_certificate'),

    url(r'^file-certificate/(?P<username>[a-zA-Z0-9_-]+)/$',
        ObjectDownloadView.as_view(
            model=User,
            file_field='high_school_certificate'),
        name='high_school_certificate'),

    url(r'^file-government_id/(?P<username>[a-zA-Z0-9_-]+)/$',
        ObjectDownloadView.as_view(
            model=User,
            file_field='government_id_file'),
        name='government_id_file'),

    url(r'^file-mother_gov_id/(?P<username>[a-zA-Z0-9_-]+)/$',
        ObjectDownloadView.as_view(
            model=User,
            file_field='mother_gov_id_file'),
        name='mother_gov_id_file'),

    url(r'^file-passport/(?P<username>[a-zA-Z0-9_-]+)/$',
        ObjectDownloadView.as_view(
            model=User,
            file_field='passport_file'),
        name='passport_file'),

    url(r'^file-personal_picture/(?P<username>[a-zA-Z0-9_-]+)/$',
        ObjectDownloadView.as_view(
            model=User,
            file_field='personal_picture'),
        name='personal_picture'),

    url(r'^file-courses_certificate/(?P<username>[a-zA-Z0-9_-]+)/$',
        ObjectDownloadView.as_view(
            model=User,
            file_field='courses_certificate'),
        name='courses_certificate'),
]
