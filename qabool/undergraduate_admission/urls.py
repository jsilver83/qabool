from django.contrib.auth.views import *
# .views import login, logout, password_change, password_change_done
from django.urls import path

from .forms.general_forms import MyPasswordChangeForm
from .views import general_views, phase1_views, phase2_views, phase3_views, admin_side_views

app_name = 'undergraduate_admission'

urlpatterns = [
    path('login/', general_views.IndexView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout', kwargs={'next_page': '/'}),
    path(
        'change-password/',
        PasswordChangeView.as_view(template_name='undergraduate_admission/change_password.html',
                                   form_class=MyPasswordChangeForm,
                                   success_url=reverse_lazy('undergraduate_admission:password_change_done')),
        name='change_password',
    ),
    path(
        'change-password-done/',
        PasswordChangeDoneView.as_view(template_name='undergraduate_admission/change_password_done.html'),
        name='password_change_done',
    ),
    path('print-tarifi-schedule/', phase3_views.PrintTarifiSchedule.as_view(), name='print_tarifi_schedule'),
    path('choose-tarifi-time-slot/', phase3_views.ChooseTarifiTimeSlot.as_view(), name='choose_tarifi_time_slot'),
    # path('admin/send-mass-sms/', admin_side_views.SendMassSMSView.as_view(), name='send_mass_sms'),
    # path('admin/student-gender/', admin_side_views.StudentGenderView.as_view(), name='student_gender'),
    path('admin/verify/<int:pk>/', admin_side_views.VerifyStudent.as_view(), name='verify_student'),
    path('admin/verify-list/new', admin_side_views.VerifyListNew.as_view(), name='verify_list_new'),
    path('admin/verify-list/pending', admin_side_views.VerifyListPendingWithStudent.as_view(), name='verify_list_with_student'),
    path('admin/verify-list/corrected', admin_side_views.VerifyListCorrectedByStudent.as_view(), name='verify_list_corrected_by_student'),
    path('admin/cutoff-point/', admin_side_views.CutOffPointView.as_view(), name='cut_off_point'),
    path('admin/distribute-committee/', admin_side_views.DistributeStudentsOnVerifiersView.as_view(),
         name='distribute_committee'),
    path('admin/yesser-sync/<int:manual_update>/<int:overwrite_update>/', admin_side_views.YesserDataUpdate.as_view(), name='yesser_update'),
    path('admin/distribute-tarifi/<int:send_sms>/', admin_side_views.TarifiDistributeView.as_view(), name='distribute_tarifi'),
    path('admin/qiyas-update/', admin_side_views.QiyasDataUpdate.as_view(), name='qiyas_update'),
    path('admin/transfer-import/', admin_side_views.TransferImportView.as_view(), name='transfer_import'),
    path('admin/smart-card-export/', admin_side_views.SmartCardExportView.as_view(), name='smart_card_export'),
    path('admin/yesser-data-fetch/', admin_side_views.YesserDataFetchView.as_view(), name='yesser_data_fetch'),
    path('withdrawal-letter/', phase2_views.WithdrawalLetterView.as_view(), name='withdrawal_letter'),
    path('withdraw/', phase2_views.WithdrawView.as_view(), name='withdraw'),
    path('medical-letter/', phase3_views.AdmissionLetters.as_view(), name='medical_letter'),
    path('admission-letter/', phase3_views.AdmissionLetters.as_view(), name='admission_letter'),
    path('print-documents2/', phase3_views.AdmissionLetters.as_view(), name='print_documents_after_phase3'),
    path('print-documents/', phase3_views.AdmissionLetters.as_view(), name='print_documents'),
    # path('studentagreement5/', phase3_views.student_agreement_5, name='student_agreement_5'),
    path('student-agreement4/', phase3_views.StudentAgreement4.as_view(), name='student_agreement_4'),
    path('student-agreement3/', phase3_views.StudentAgreement3.as_view(), name='student_agreement_3'),
    path('student-agreement2/', phase3_views.StudentAgreement2.as_view(), name='student_agreement_2'),
    path('student-agreement1/', phase3_views.StudentAgreement1.as_view(), name='student_agreement_1'),
    path('upload-documents-incomplete/', phase2_views.UploadMissingDocumentsView.as_view(),
         name='upload_documents_incomplete'),
    path('upload-withdrawal-proof/', phase2_views.UploadWithdrawalProofView.as_view(), name='upload_withdrawal_proof'),
    path('personal-picture/', phase2_views.PersonalPictureView.as_view(), name='personal_picture'),
    path('personal-picture-re-upload/', phase2_views.PersonalPictureUnacceptableView.as_view(),
         name='personal_picture_re_upload'),
    path('upload-documents/', phase2_views.UploadDocumentsView.as_view(), name='upload_documents'),
    # path('compare-names/', phase2_views.CompareNamesView.as_view(), name='compare_names'),
    path('relative-contact/', phase2_views.RelativeContactView.as_view(), name='relative_contact'),
    path('guardian-contact/', phase2_views.GuardianContactView.as_view(), name='guardian_contact'),
    path('personal-info/', phase2_views.PersonalInfoView.as_view(), name='personal_info'),
    path('confirm/', phase2_views.Confirm.as_view(), name='confirm'),
    path('edit-info/', phase1_views.EditInfo.as_view(), name='edit_info'),
    path('edit-contact-info/', general_views.EditContactInfo.as_view(), name='edit_contact_info'),
    path('transfer/', phase2_views.TransferView.as_view(), name='transfer'),
    path('register/', phase1_views.RegisterView.as_view(), name='register'),
    path('student-area/', general_views.StudentArea.as_view(), name='student_area'),
    path('registration-success/', phase1_views.RegistrationSuccess.as_view(), name='registration_success'),
    path('initial-agreement/', phase1_views.initial_agreement, name='initial_agreement'),
    path('forgot-password/', general_views.ForgotPassword.as_view(), name='forgot_password'),
    path('', general_views.IndexView.as_view(), name='index'),
]
