from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from undergraduate_admission.forms.phase1_forms import AgreementForm
from undergraduate_admission.forms.phase3_forms import TarifiTimeSlotForm
from undergraduate_admission.models import AdmissionSemester, Agreement, RegistrationStatusMessage, KFUPMIDsPool
from undergraduate_admission.utils import SMS


def is_phase3_eligible(user):
    return user.status_message == RegistrationStatusMessage.get_status_admitted()


@login_required()
@user_passes_test(is_phase3_eligible)
def student_agreement_1(request):
    form = AgreementForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            request.session['agreed1'] = True
            return redirect('student_agreement_2')
        else:
            messages.error(request, _('Error.'))

    sem = AdmissionSemester.get_phase3_active_semester(request.user)
    agreement = get_object_or_404(Agreement, agreement_type='STUDENT_AGREEMENT_1', semester=sem)
    agreement_items = agreement.items.filter(show=True)
    return render(request, 'undergraduate_admission/phase2/student_agreement.html', {'agreement': agreement,
                                                                                     'items': agreement_items,
                                                                                     'form': form,
                                                                                     'step1': 'active'})


@login_required()
@user_passes_test(is_phase3_eligible)
def student_agreement_2(request):
    form = AgreementForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            request.session['agreed2'] = True
            return redirect('student_agreement_3')
        else:
            messages.error(request, _('Error.'))

    sem = AdmissionSemester.get_phase3_active_semester(request.user)
    agreement = get_object_or_404(Agreement, agreement_type='STUDENT_AGREEMENT_2', semester=sem)
    agreement_items = agreement.items.filter(show=True)
    return render(request, 'undergraduate_admission/phase2/student_agreement.html', {'agreement': agreement,
                                                                                     'items': agreement_items,
                                                                                     'form': form,
                                                                                     'step2': 'active'})


@login_required()
@user_passes_test(is_phase3_eligible)
def student_agreement_3(request):
    form = AgreementForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            request.session['agreed3'] = True
            return redirect('student_agreement_4')
        else:
            messages.error(request, _('Error.'))

    sem = AdmissionSemester.get_phase3_active_semester(request.user)
    agreement = get_object_or_404(Agreement, agreement_type='STUDENT_AGREEMENT_3', semester=sem)
    agreement_items = agreement.items.filter(show=True)
    return render(request, 'undergraduate_admission/phase2/student_agreement.html', {'agreement': agreement,
                                                                                     'items': agreement_items,
                                                                                     'form': form,
                                                                                     'step3': 'active'})


@login_required()
@user_passes_test(is_phase3_eligible)
def student_agreement_4(request):
    form = AgreementForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            request.session['agreed4'] = True
            return redirect('choose_tarifi_time_slot')
        else:
            messages.error(request, _('Error.'))

    sem = AdmissionSemester.get_phase3_active_semester(request.user)
    agreement = get_object_or_404(Agreement, agreement_type='STUDENT_AGREEMENT_4', semester=sem)
    agreement_items = agreement.items.filter(show=True)
    return render(request, 'undergraduate_admission/phase2/student_agreement.html', {'agreement': agreement,
                                                                                     'items': agreement_items,
                                                                                     'form': form,
                                                                                     'step4': 'active'})


@login_required()
@user_passes_test(is_phase3_eligible)
def choose_tarifi_time_slot(request):
    form = TarifiTimeSlotForm(request.POST or None, instance=request.user)

    if request.user.tarifi_week_attendance_date:
        return redirect('student_area')

    if request.method == 'POST':
        if form.is_valid():
            kfupm_id = KFUPMIDsPool.get_next_available_id()

            if kfupm_id:
                saved = form.save(commit=False)
                saved.phase3_submit_date = timezone.now()
                if not saved.kfupm_id:
                    saved.kfupm_id = kfupm_id
                saved.save()

                if saved:
                    messages.success(request, _('Tarifi time slot was chosen successfully...'))
                    SMS.send_sms_admitted(request.user.mobile)
                    return redirect('print_documents')
                else:
                    messages.error(request, _('Error saving info. Try again later!'))
            else:
                messages.error(request, _('No IDs to assign. Contact the site admins...'))
                return redirect('choose_tarifi_time_slot')
        else:
            print(form.errors)
            messages.error(request, _('Error.'))

    return render(request, 'undergraduate_admission/phase3/tarifi_time_slot.html', {'form': form, })


@login_required()
@user_passes_test(is_phase3_eligible)
def print_documents(request):
    eligible_for_housing = request.user.eligible_for_housing
    return render(request, 'undergraduate_admission/phase2/print_documents.html',
                  {'eligible_for_housing': eligible_for_housing, })


@login_required()
@user_passes_test(is_phase3_eligible)
def admission_letter(request):
    if request.method == "GET" and not request.user.admission_letter_print_date:
        request.user.admission_letter_print_date = timezone.now()
        request.user.save()

    user = request.user

    return render(request, 'undergraduate_admission/phase2/letter_admission.html', {'user': user,})


@login_required()
@user_passes_test(is_phase3_eligible)
def medical_letter(request):
    if request.method == "GET" and not request.user.medical_report_print_date:
        request.user.medical_report_print_date = timezone.now()
        request.user.save()

    user = request.user

    return render(request, 'undergraduate_admission/phase2/letter_medical.html', {'user': user,})