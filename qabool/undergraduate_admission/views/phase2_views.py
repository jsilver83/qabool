from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.base import View
from django.http import Http404

from sendfile import sendfile, os

from qabool.local_settings import SENDFILE_ROOT
from undergraduate_admission.forms.phase1_forms import AgreementForm, BaseAgreementForm
from undergraduate_admission.forms.phase2_forms import PersonalInfoForm, DocumentsForm, GuardianContactForm, \
    RelativeContactForm, WithdrawalForm, WithdrawalProofForm
from undergraduate_admission.models import AdmissionSemester, Agreement, RegistrationStatusMessage, KFUPMIDsPool
from undergraduate_admission.models import User
from undergraduate_admission.utils import SMS
from undergraduate_admission.validators import is_eligible_for_roommate_search


def is_phase2_eligible(user):
    phase = user.get_student_phase()
    return phase == 'PARTIALLY-ADMITTED'


def is_admitted(user):
    phase = user.get_student_phase()
    return phase == 'ADMITTED'


def is_withdrawn(user):
    phase = user.get_student_phase()
    return phase == 'WITHDRAWN'


def is_eligible_to_withdraw(user):
    return is_admitted(user) and not user.tarifi_week_attendance_date


class UserFileView(LoginRequiredMixin, UserPassesTestMixin, View):
    raise_exception = True  # PermissionDenied

    def test_func(self):
        return self.request.user.is_staff or self.request.user.id == int(self.kwargs['pk']) \
               or is_eligible_for_roommate_search(self.request.user)

    def get(self, request, filetype, pk):
        user = get_object_or_404(User, pk=pk)
        try:
            user_file = getattr(user, filetype)
        except AttributeError:  # invalid filetype
            raise Http404
        if not user_file:       # file not uploaded
            raise Http404
        return sendfile(request, user_file.path)


@login_required()
def media_view(request, filename):
    user = request.user
    absolute_file_name = os.path.join(SENDFILE_ROOT, filename)

    if user.is_staff:
        return sendfile(request, absolute_file_name)
    else:
        if filename.startswith('govid/'):
            if user.government_id_file == filename:
                return sendfile(request, user.government_id_file.path)

        elif filename.startswith('picture/'):
            if user.personal_picture == filename:
                return sendfile(request, user.personal_picture.path)

        elif filename.startswith('certificate/courses'):
            if user.courses_certificate == filename:
                return sendfile(request, user.courses_certificate.path)

        elif filename.startswith('certificate/'):
            if user.high_school_certificate == filename:
                return sendfile(request, user.high_school_certificate.path)

        elif filename.startswith('birth/'):
            if user.birth_certificate == filename:
                return sendfile(request, user.birth_certificate.path)

        elif filename.startswith('mother_govid/'):
            if user.mother_gov_id_file == filename:
                return sendfile(request, user.mother_gov_id_file.path)

        elif filename.startswith('passport/'):
            if user.passport_file == filename:
                return sendfile(request, user.passport_file.path)

        elif filename.startswith('withdrawal_proof/'):
            if user.withdrawal_proof_letter == filename:
                return sendfile(request, user.withdrawal_proof_letter.path)

        else:
            raise PermissionDenied


@login_required()
@user_passes_test(is_phase2_eligible)
def confirm(request):
    form = BaseAgreementForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            request.session['confirmed'] = True
            return redirect('personal_info')
        else:
            messages.error(request, _('Error.'))

    sem = AdmissionSemester.get_phase2_active_semester(request.user)
    agreement = get_object_or_404(Agreement, agreement_type='CONFIRM', semester=sem)
    agreement_items = agreement.items.filter(show=True)
    return render(request, 'undergraduate_admission/phase2/confirm.html', {'agreement': agreement,
                                                                           'items': agreement_items,
                                                                           'form': form,})


@login_required()
@user_passes_test(is_phase2_eligible)
def personal_info(request):
    form = PersonalInfoForm(request.POST or None,
                            instance=request.user, )

    if request.method == 'GET':
        confirmed = request.session.get('confirmed')
        if confirmed is None:
            return redirect('confirm')

    if request.method == 'POST':
        if form.is_valid():
            saved = form.save()
            if saved:
                messages.success(request, _('Personal Info was saved successfully...'))
                request.session['personal_info_completed'] = True
                return redirect('guardian_contact')
            else:
                messages.error(request, _('Error saving info. Try again later!'))

    return render(request, 'undergraduate_admission/phase2/form-personal.html', {'form': form,
                                                                                 'step1': 'active'})


@login_required()
@user_passes_test(is_phase2_eligible)
def guardian_contact(request):
    if request.method == 'GET':
        personal_info_completed = request.session.get('personal_info_completed')
        if not personal_info_completed:
            return redirect('personal_info')

    form = GuardianContactForm(request.POST or None, instance=request.user)

    if request.method == 'POST':
        if form.is_valid():
            saved = form.save()
            if saved:
                messages.success(request, _('Guardian Contact Info was saved successfully...'))
                request.session['guardian_contact_completed'] = True
                return redirect('relative_contact')
            else:
                messages.error(request, _('Error saving info. Try again later!'))

    return render(request, 'undergraduate_admission/phase2/form.html', {'form': form,
                                                                        'step2': 'active'})


@login_required()
@user_passes_test(is_phase2_eligible)
def relative_contact(request):
    if request.method == 'GET':
        guardian_contact_completed = request.session.get('guardian_contact_completed')
        if not guardian_contact_completed:
            return redirect('guardian_contact')

    form = RelativeContactForm(request.POST or None, instance=request.user)

    if request.method == 'POST':
        if form.is_valid():
            saved = form.save()
            if saved:
                messages.success(request, _('Relative Info was saved successfully...'))
                request.session['relative_contact_completed'] = True
                return redirect('upload_documents')
            else:
                messages.error(request, _('Error saving info. Try again later!'))

    return render(request, 'undergraduate_admission/phase2/form-relative.html', {'form': form,
                                                                                 'step3': 'active'})


@login_required()
@user_passes_test(is_phase2_eligible)
def upload_documents(request):
    if request.method == 'GET':
        relative_contact_completed = request.session.get('relative_contact_completed')
        if not relative_contact_completed:
            return redirect('relative_contact')

    form = DocumentsForm(request.POST or None, request.FILES or None, instance=request.user)

    if request.method == 'POST':
        if form.is_valid():
            saved = form.save()
            if saved:
                messages.success(request, _('Documents were uploaded successfully...'))
                request.session['upload_documents_completed'] = True
                return redirect('student_agreement_1')
            else:
                messages.error(request, _('Error saving info. Try again later!'))

    return render(request, 'undergraduate_admission/phase2/form-uploads.html', {'form': form,
                                                                                'step4': 'active'})


@login_required()
def upload_documents_for_incomplete(request):
    # it is ok to come here unconditionally if uploaded docs are incomplete
    if request.method == 'GET' and not request.user.verification_documents_incomplete:
        return redirect('student_area')

    form = DocumentsForm(request.POST or None, request.FILES or None, instance=request.user)

    if request.method == 'POST':
        if form.is_valid():
            saved = form.save()
            if saved:
                messages.success(request, _('Documents were uploaded successfully...'))
                request.session['upload_documents_completed'] = True
                return redirect('student_agreement_1')
            else:
                messages.error(request, _('Error saving info. Try again later!'))

    return render(request, 'undergraduate_admission/phase2/plain_form.html', {'form': form, })


@login_required()
def upload_withdrawal_proof(request):
    # it is ok to come here unconditionally if student has duplicate admission in other universities
    if request.method == 'GET' and not request.user.status_message == RegistrationStatusMessage.get_status_duplicate():
        return redirect('student_area')

    form = WithdrawalProofForm(request.POST or None, request.FILES or None, instance=request.user)

    if request.method == 'POST':
        if form.is_valid():
            saved = form.save()
            if saved:
                messages.success(request, _('Documents were uploaded successfully...'))
                request.session['upload_documents_completed'] = True
                return redirect('student_area')
            else:
                messages.error(request, _('Error saving info. Try again later!'))

    return render(request, 'undergraduate_admission/phase2/plain_form.html', {'form': form, })


@login_required()
@user_passes_test(is_phase2_eligible)
def student_agreement_1(request):
    form = AgreementForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            request.session['agreed1'] = True
            return redirect('student_agreement_2')
        else:
            messages.error(request, _('Error.'))

    sem = AdmissionSemester.get_phase2_active_semester(request.user)
    agreement = get_object_or_404(Agreement, agreement_type='STUDENT_AGREEMENT_1', semester=sem)
    agreement_items = agreement.items.filter(show=True)
    return render(request, 'undergraduate_admission/phase2/student_agreement.html', {'agreement': agreement,
                                                                                     'items': agreement_items,
                                                                                     'form': form,
                                                                                     'step1': 'active'})


@login_required()
@user_passes_test(is_phase2_eligible)
def student_agreement_2(request):
    form = AgreementForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            request.session['agreed2'] = True
            return redirect('student_agreement_3')
        else:
            messages.error(request, _('Error.'))

    sem = AdmissionSemester.get_phase2_active_semester(request.user)
    agreement = get_object_or_404(Agreement, agreement_type='STUDENT_AGREEMENT_2', semester=sem)
    agreement_items = agreement.items.filter(show=True)
    return render(request, 'undergraduate_admission/phase2/student_agreement.html', {'agreement': agreement,
                                                                                     'items': agreement_items,
                                                                                     'form': form,
                                                                                     'step2': 'active'})


@login_required()
@user_passes_test(is_phase2_eligible)
def student_agreement_3(request):
    form = AgreementForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            request.session['agreed3'] = True
            return redirect('student_agreement_4')
        else:
            messages.error(request, _('Error.'))

    sem = AdmissionSemester.get_phase2_active_semester(request.user)
    agreement = get_object_or_404(Agreement, agreement_type='STUDENT_AGREEMENT_3', semester=sem)
    agreement_items = agreement.items.filter(show=True)
    return render(request, 'undergraduate_admission/phase2/student_agreement.html', {'agreement': agreement,
                                                                                     'items': agreement_items,
                                                                                     'form': form,
                                                                                     'step3': 'active'})


@login_required()
@user_passes_test(is_phase2_eligible)
def student_agreement_4(request):
    form = AgreementForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            request.session['agreed5'] = True

            reg_msg = RegistrationStatusMessage.get_status_admitted()
            kfupm_id = KFUPMIDsPool.get_next_available_id()

            user = request.user
            if not user.kfupm_id:
                user.kfupm_id = kfupm_id
            user.status_message = reg_msg
            user.save()

            SMS.send_sms_admitted(user.mobile)

            return redirect('print_documents')
        else:
            messages.error(request, _('Error.'))

    sem = AdmissionSemester.get_phase2_active_semester(request.user)
    agreement = get_object_or_404(Agreement, agreement_type='STUDENT_AGREEMENT_4', semester=sem)
    agreement_items = agreement.items.filter(show=True)
    return render(request, 'undergraduate_admission/phase2/student_agreement.html', {'agreement': agreement,
                                                                                     'items': agreement_items,
                                                                                     'form': form,
                                                                                     'step4': 'active'})


@login_required()
@user_passes_test(is_admitted)
def print_documents(request):
    eligible_for_housing = request.user.eligible_for_housing
    return render(request, 'undergraduate_admission/phase2/print_documents.html',
                  {'eligible_for_housing': eligible_for_housing, })


@login_required()
@user_passes_test(is_eligible_to_withdraw)
def withdraw(request):
    form = WithdrawalForm(request.POST or None, instance=request.user)

    if request.method == "GET":
        if request.user.get_student_phase() == 'WITHDRAWN':
            return redirect("withdrawal_letter")

    if request.method == 'POST':
        if form.is_valid():
            saved = form.save()
            if saved:
                messages.success(request, _('You have withdrawn from the university successfully...'))

                SMS.send_sms_withdrawn(request.user.mobile)

                return redirect('withdrawal_letter')
            else:
                messages.error(request, _('Error saving info. Try again later!'))

    return render(request, 'undergraduate_admission/phase2/withdraw.html', {'form': form,})


@login_required()
@user_passes_test(is_withdrawn)
def withdrawal_letter(request):
    if request.method == "GET" and request.user.get_student_phase() != 'WITHDRAWN':
        return redirect("student_area")

    user = request.user

    return render(request, 'undergraduate_admission/phase2/letter_withdrawal.html', {'user': user,})


@login_required()
@user_passes_test(is_admitted)
def admission_letter(request):
    if request.method == "GET" and not request.user.admission_letter_print_date:
        request.user.admission_letter_print_date = timezone.now()
        request.user.save()

    user = request.user

    return render(request, 'undergraduate_admission/phase2/letter_admission.html', {'user': user,})


@login_required()
@user_passes_test(is_admitted)
def medical_letter(request):
    if request.method == "GET" and not request.user.medical_report_print_date:
        request.user.medical_report_print_date = timezone.now()
        request.user.save()

    user = request.user

    return render(request, 'undergraduate_admission/phase2/letter_medical.html', {'user': user,})