from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import UpdateView
from django.views.generic.base import View
from django.http import Http404
from django.views.decorators.cache import never_cache

from sendfile import sendfile, os

from qabool.local_settings import SENDFILE_ROOT
from undergraduate_admission.forms.phase1_forms import AgreementForm, BaseAgreementForm
from undergraduate_admission.forms.phase2_forms import PersonalInfoForm, DocumentsForm, GuardianContactForm, \
    RelativeContactForm, WithdrawalForm, WithdrawalProofForm, VehicleInfoForm, PersonalPhotoForm
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
    return user.status_message == RegistrationStatusMessage.get_status_admitted() \
           or user.status_message == RegistrationStatusMessage.get_status_confirmed()


@method_decorator(never_cache, name='dispatch')
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
        if not user_file:  # file not uploaded
            raise Http404
        return sendfile(request, user_file.path)


class Phase2BaseView(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return is_phase2_eligible(self.request.user)


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
                                                                           'form': form, })


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
                return redirect('vehicle_info')
            else:
                messages.error(request, _('Error saving info. Try again later!'))

    return render(request, 'undergraduate_admission/phase2/form-relative.html', {'form': form,
                                                                                 'step3': 'active'})


@login_required()
@user_passes_test(is_phase2_eligible)
def vehicle_info(request):
    if request.method == 'GET':
        relative_contact_completed = request.session.get('relative_contact_completed')
        if not relative_contact_completed:
            return redirect('relative_contact')

    form = VehicleInfoForm(request.POST or None, request.FILES or None, instance=request.user)

    if request.method == 'POST':
        if form.is_valid():
            saved = form.save()
            if saved:
                messages.success(request, _('Vehicle info was submitted successfully...'))
                request.session['vehicle_info_completed'] = True
                return redirect('personal_picture')
            else:
                messages.error(request, _('Error saving info. Try again later!'))

    return render(request, 'undergraduate_admission/phase2/form-uploads.html', {'form': form,
                                                                                'step4': 'active'})


class PersonalPictureView(Phase2BaseView, UpdateView):
    template_name = 'undergraduate_admission/phase2/form-personal-picture.html'
    form_class = PersonalPhotoForm
    success_url = reverse_lazy('personal_picture')

    def test_func(self):
        original_test_result = super(PersonalPictureView, self).test_func()
        relative_contact_completed = self.request.session.get('relative_contact_completed')
        return original_test_result and relative_contact_completed

    def get_context_data(self, **kwargs):
        context = super(PersonalPictureView, self).get_context_data(**kwargs)
        context['step5'] = 'active'
        context['base_extend'] = 'undergraduate_admission/phase2/form.html'
        context['re_upload'] = False
        return context

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        super(PersonalPictureView, self).form_valid(form)
        saved = form.save()
        if saved:
            messages.success(self.request, _('Personal picture was uploaded successfully...'))
            self.request.session['personal_picture_completed'] = True
            return redirect(self.success_url)
        else:
            messages.error(self.request, _('Error saving info. Try again later!'))


class PersonalPictureUnacceptableView(Phase2BaseView, UpdateView):
    template_name = 'undergraduate_admission/phase2/form-personal-picture.html'
    form_class = PersonalPhotoForm
    success_url = reverse_lazy('personal_picture_re_upload')

    def test_func(self):
        original_test_result = super(PersonalPictureUnacceptableView, self).test_func()
        can_re_upload_picture = self.request.user.verification_picture_acceptable
        return original_test_result and can_re_upload_picture

    def get_context_data(self, **kwargs):
        context = super(PersonalPictureUnacceptableView, self).get_context_data(**kwargs)
        context['base_extend'] = 'base_student_area.html'
        context['re_upload'] = True
        return context

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        super(PersonalPictureUnacceptableView, self).form_valid(form)
        saved = form.save()
        if saved:
            messages.success(self.request, _('Personal picture was uploaded successfully...'))
            self.request.session['personal_picture_completed'] = True
            return redirect(self.success_url)
        else:
            messages.error(self.request, _('Error saving info. Try again later!'))


@login_required()
@user_passes_test(is_phase2_eligible)
def upload_documents(request):
    if request.method == 'GET':
        personal_picture_completed = request.GET.get('f', '')
        if not personal_picture_completed:
            return redirect('personal_picture')

    form = DocumentsForm(request.POST or None, request.FILES or None, instance=request.user)

    if request.method == 'POST':
        if form.is_valid():
            reg_msg = RegistrationStatusMessage.get_status_confirmed()

            saved_user = form.save(commit=False)
            saved_user.status_message = reg_msg
            saved_user.save()

            if saved_user:
                SMS.send_sms_confirmed(request.user.mobile)
                messages.success(request, _('Documents were uploaded successfully. We will verify your information '
                                            'and get back to you soon...'))
                return redirect('student_area')
            else:
                messages.error(request, _('Error saving info. Try again later!'))

    return render(request, 'undergraduate_admission/phase2/form-uploads.html', {'form': form,
                                                                                'step6': 'active'})


@login_required()
@user_passes_test(is_phase2_eligible)
def upload_documents_for_incomplete(request):
    # it is ok to come here unconditionally if uploaded docs are incomplete
    if request.method == 'GET' and not request.user.verification_documents_incomplete:
        return redirect('student_area')

    form = DocumentsForm(request.POST or None, request.FILES or None, instance=request.user)

    if request.method == 'POST':
        if form.is_valid():
            saved = form.save()
            if saved:
                messages.success(request, _('Documents were uploaded successfully. We will verify your information '
                                            'and get back to you soon...'))
                return redirect('student_area')
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

    return render(request, 'undergraduate_admission/phase2/withdraw.html', {'form': form, })


@login_required()
@user_passes_test(is_withdrawn)
def withdrawal_letter(request):
    if request.method == "GET" and request.user.get_student_phase() != 'WITHDRAWN':
        return redirect("student_area")

    user = request.user

    return render(request, 'undergraduate_admission/phase2/letter_withdrawal.html', {'user': user, })
