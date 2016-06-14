from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from undergraduate_admission.forms.phase1_forms import AgreementForm, BaseAgreementForm
from undergraduate_admission.forms.phase2_forms import PersonalInfoForm, DocumentsForm, GuardianContactForm, \
    RelativeContactForm, WithdrawalForm
from undergraduate_admission.models import AdmissionSemester, Agreement, RegistrationStatusMessage, KFUPMIDsPool


def is_phase2_eligible(user):
    phase = user.get_student_phase()
    return phase == 'PARTIALLY-ADMITTED'


def is_admitted(user):
    phase = user.get_student_phase()
    return phase == 'ADMITTED'


@login_required()
def confirm(request):
    form = BaseAgreementForm(request.POST or None)

    if request.method == 'GET' and not is_phase2_eligible(request.user):
        return redirect('student_area')

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
def personal_info(request):
    form = PersonalInfoForm(request.POST or None,
                            instance=request.user,)

    if request.method == 'GET':
        confirmed = request.session.get('confirmed')
        if confirmed is None:
            return redirect('confirm')

        if not is_phase2_eligible(request.user):
            return redirect('student_area')

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
def guardian_contact(request):
    if request.method == 'GET':
        personal_info_completed = request.session.get('personal_info_completed')
        if not personal_info_completed :
            return redirect('personal_info')

        if not is_phase2_eligible(request.user):
            return redirect('student_area')

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
def relative_contact(request):
    if request.method == 'GET':
        guardian_contact_completed = request.session.get('guardian_contact_completed')
        if not guardian_contact_completed:
            return redirect('guardian_contact')

        if not is_phase2_eligible(request.user):
            return redirect('student_area')

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
def upload_documents(request):
    if request.method == 'GET':
        relative_contact_completed = request.session.get('relative_contact_completed')
        if not relative_contact_completed:
            return redirect('relative_contact')

        if not is_phase2_eligible(request.user):
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

    return render(request, 'undergraduate_admission/phase2/form-uploads.html', {'form': form,
                                                                                'step4': 'active'})


@login_required()
def student_agreement_1(request):
    if request.method == 'GET' and not is_phase2_eligible(request.user):
        return redirect('student_area')

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
def student_agreement_2(request):
    if request.method == 'GET' and not is_phase2_eligible(request.user):
        return redirect('student_area')

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
def student_agreement_3(request):
    if request.method == 'GET' and not is_phase2_eligible(request.user):
        return redirect('student_area')

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
def student_agreement_4(request):
    if request.method == 'GET' and not is_phase2_eligible(request.user):
        return redirect('student_area')

    form = AgreementForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            request.session['agreed5'] = True

            reg_msg = RegistrationStatusMessage.get_status_admitted()
            kfupm_id = KFUPMIDsPool.get_next_available_id()

            user = request.user
            user.kfupm_id = kfupm_id
            user.status_message = reg_msg
            user.save()

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
def print_documents(request):
    if request.method == 'GET' and not is_admitted(request.user):
        return redirect('student_area')

    return render(request, 'undergraduate_admission/phase2/print_documents.html')


@login_required()
def withdraw(request):
    form = WithdrawalForm(request.POST or None, instance=request.user)

    if request.method == "GET":
        if request.user.get_student_phase() == 'WITHDRAWN':
            return redirect("withdrawal_letter")

        if request.user.get_student_phase() != 'ADMITTED':
            return redirect('student_area')

    if request.method == 'POST':
        if form.is_valid():
            saved = form.save()
            if saved:
                messages.success(request, _('You have withdrawn from the university successfully...'))
                return redirect('withdrawal_letter')
            else:
                messages.error(request, _('Error saving info. Try again later!'))

    return render(request, 'undergraduate_admission/phase2/withdraw.html', {'form': form,})


# @login_required()
# def withdrawal_letter(request):
#     user=request.user
#
#     return render(request, 'undergraduate_admission/phase2/letter_withdrawal.html', {'user': user,})


@login_required()
def withdrawal_letter(request):
    if request.method == "GET":
        if request.user.get_student_phase() != 'WITHDRAWN':
            return redirect("student_area")

    user = request.user

    return render(request, 'undergraduate_admission/phase2/letter_withdrawal.html', {'user': user,})


@login_required()
def admission_letter(request):
    if request.method == "GET":
        if not is_admitted(request.user):
            return redirect("student_area")
        if not request.user.admission_letter_print_date:
            request.user.admission_letter_print_date = timezone.now()
            request.user.save()

    user = request.user

    return render(request, 'undergraduate_admission/phase2/letter_admission.html', {'user': user, })


@login_required()
def medical_letter(request):
    # if request.method == "GET":
    #     if not is_admitted(request.user):
    #         return redirect("student_area")
    #     if not request.user.medical_report_print_date:
    #         request.user.medical_report_print_date = timezone.now()
    #         request.user.save()

    user = request.user

    return render(request, 'undergraduate_admission/phase2/letter_medical.html', {'user': user, })