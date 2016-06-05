from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.translation import ugettext_lazy as _

from undergraduate_admission.forms.phase1_forms import AgreementForm
from undergraduate_admission.forms.phase2_forms import PersonalInfoForm, DocumentsForm, GuardianContactForm, \
    RelativeContactForm
from undergraduate_admission.models import AdmissionSemester, Agreement


@login_required()
def confirm(request):
    form = AgreementForm(request.POST or None)

    if request.method == 'GET':
        # check if student is eligible
        pass

    if request.method == 'POST':
        if form.is_valid():
            request.session['confirmed'] = True
            return redirect('personal_info')
        else:
            messages.error(request, _('Error.'))

    sem = AdmissionSemester.get_phase2_active_semester(request.user)
    agreement = get_object_or_404(Agreement, agreement_type='CONFIRM', semester=sem)
    agreement_items = agreement.items.filter(show=True)
    return render(request, 'undergraduate_admission/phase2/agreement.html', {'agreement': agreement,
                                                                             'items': agreement_items,
                                                                             'form': form,})


@login_required()
def personal_info(request):
    confirmed = request.session.get('confirmed')
    if confirmed is None:
        return redirect('confirm')

    form = PersonalInfoForm(request.POST or None, instance=request.user)

    if request.method == 'POST':
        if form.is_valid():
            saved = form.save()
            if saved:
                messages.success(request, _('Personal Info was saved successfully...'))
                request.session['personal_info_completed'] = True
                return redirect('guardian_contact')
            else:
                messages.error(request, _('Error saving info. Try again later!'))

    return render(request, 'undergraduate_admission/phase2/form.html', {'form': form,
                                                                        'step1': 'active'})


@login_required()
def guardian_contact(request):
    # personal_info_completed = request.session.get('personal_info_completed')
    # if personal_info_completed is None:
    #     return redirect('personal_info')

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
    # guardian_contact_completed = request.session.get('guardian_contact_completed')
    # if guardian_contact_completed is None:
    #     return redirect('guardian_contact')

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

    return render(request, 'undergraduate_admission/phase2/form.html', {'form': form,
                                                                        'step3': 'active'})


@login_required()
def upload_documents(request):
    # relative_contact_completed = request.session.get('relative_contact_completed')
    # if relative_contact_completed is None:
    #     return redirect('relative_contact')

    form = DocumentsForm(request.POST or None, request.FILES or None, instance=request.user)

    if request.method == 'POST':
        if form.is_valid():
            saved = form.save()
            if saved:
                messages.success(request, _('Documents were uploaded successfully...'))
                request.session['upload_documents_completed'] = True
                return redirect('upload_documents')
            else:
                messages.error(request, _('Error saving info. Try again later!'))

    return render(request, 'undergraduate_admission/phase2/form.html', {'form': form,
                                                                        'step4': 'active'})
