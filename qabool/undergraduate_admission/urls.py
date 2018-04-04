from django.conf.urls import url, include
from django.contrib.auth.views import login, logout, password_change, password_change_done

from .views import general_views, phase1_views, phase2_views, phase3_views, admin_side_views
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

    url(r'^choosetarifitimeslot/$', phase3_views.ChooseTarifiTimeSlot.as_view(), name='choose_tarifi_time_slot'),
    url(r'^admin/sendmasssms/$', admin_side_views.SendMassSMSView.as_view(), name='send_mass_sms'),
    url(r'^admin/studentgender/$', admin_side_views.StudentGenderView.as_view(), name='student_gender'),
    url(r'^admin/verify/(?P<pk>\d+)/$', admin_side_views.VerifyStudent.as_view(), name='verify_student'),
    url(r'^admin/verifylist/$', admin_side_views.VerifyList.as_view(), name='verify_list'),
    url(r'^admin/cutoffpoint/$', admin_side_views.CutOffPointView.as_view(), name='cut_off_point'),
    # url(r'^admin/yesserupdateb/$', admin_side_views.YesserDataUpdateBackup.as_view(), name='yesser_update_backup'),
    url(r'^admin/yesserupdate/$', admin_side_views.YesserDataUpdate.as_view(), name='yesser_update'),
    url(r'^admin/qiyasupdate/$', admin_side_views.QiyasDataUpdate.as_view(), name='qiyas_update'),
    url(r'^checkifadmitted/$', general_views.check_if_student_is_admitted, name='check_if_student_is_admitted'),
    url(r'^markasattended/$', general_views.mark_student_as_attended, name='mark_student_as_attended'),
    url(r'^withdrawalletter/$', phase2_views.withdrawal_letter, name='withdrawal_letter'),
    url(r'^withdraw/$', phase2_views.WithdrawView.as_view(), name='withdraw'),
    url(r'^medicalletter/$', phase3_views.MedicalLetter.as_view(), name='medical_letter'),
    url(r'^admissionletter/$', phase3_views.AdmissionLetter.as_view(), name='admission_letter'),
    url(r'^printdocuments2/$', phase3_views.BasePrintDocuments.as_view(), name='print_documents_after_phase3'),
    url(r'^printdocuments/$', phase3_views.PrintDocuments.as_view(), name='print_documents'),
    # url(r'^studentagreement5/$', phase3_views.student_agreement_5, name='student_agreement_5'),
    url(r'^studentagreement4/$', phase3_views.StudentAgreement4.as_view(), name='student_agreement_4'),
    url(r'^studentagreement3/$', phase3_views.StudentAgreement3.as_view(), name='student_agreement_3'),
    url(r'^studentagreement2/$', phase3_views.StudentAgreement2.as_view(), name='student_agreement_2'),
    url(r'^studentagreement1/$', phase3_views.StudentAgreement1.as_view(), name='student_agreement_1'),
    url(r'^uploaddocumentsincomplete/$', phase2_views.upload_documents_for_incomplete,
        name='upload_documents_incomplete'),
    url(r'^uploadwithdrawalproof/$', phase2_views.upload_withdrawal_proof, name='upload_withdrawal_proof'),
    url(r'^personalpicture/$', phase2_views.PersonalPictureView.as_view(), name='personal_picture'),
    url(r'^personalpicturereupload/$', phase2_views.PersonalPictureUnacceptableView.as_view(), name='personal_picture_re_upload'),
    url(r'^uploaddocuments/$', phase2_views.upload_documents, name='upload_documents'),
    url(r'^vehicleinfo/$', phase2_views.vehicle_info, name='vehicle_info'),
    url(r'^relativecontact/$', phase2_views.relative_contact, name='relative_contact'),
    url(r'^guardiancontact/$', phase2_views.guardian_contact, name='guardian_contact'),
    url(r'^personalinfo/$', phase2_views.personal_info, name='personal_info'),
    url(r'^confirm/$', phase2_views.confirm, name='confirm'),
    url(r'^editinfo/$', phase1_views.EditInfo.as_view(), name='edit_info'),
    url(r'^editcontactinfo/$', general_views.EditContactInfo.as_view(), name='edit_contact_info'),
    url(r'^register/$', phase1_views.RegisterView.as_view(), name='register'),
    url(r'^studentarea/$', general_views.student_area, name='student_area'),
    url(r'^registrationsuccess/$', phase1_views.RegistrationSuccess.as_view(), name='registration_success'),
    url(r'^initialagreement/$', phase1_views.initial_agreement, name='initial_agreement'),
    url(r'^forgotpassword/$', general_views.forgot_password, name='forgot_password'),
    url(r'^$', general_views.index, name='index'),
]
