from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import UpdateView, FormView
from django.views.generic.base import View
from django.http import Http404
from django.views.decorators.cache import never_cache

from sendfile import sendfile, os

# from find_roommate.models import RoommateRequest
from qabool.local_settings import SENDFILE_ROOT
from undergraduate_admission.forms.phase1_forms import AgreementForm, BaseAgreementForm
from undergraduate_admission.forms.phase2_forms import PersonalInfoForm, DocumentsForm, GuardianContactForm, \
    RelativeContactForm, WithdrawalForm, WithdrawalProofForm, VehicleInfoForm, PersonalPhotoForm, TransferForm, \
    MissingDocumentsForm
from undergraduate_admission.models import AdmissionSemester, Agreement, RegistrationStatusMessage, KFUPMIDsPool
from undergraduate_admission.models import User
from undergraduate_admission.utils import SMS, parse_non_standard_numerals
from undergraduate_admission.validators import is_eligible_for_roommate_search


# TODO: refactor all is_eligible_to_??? to be functions in the class User
def can_confirm(user):
    return ((user.status_message == RegistrationStatusMessage.get_status_partially_admitted() or
             user.status_message == RegistrationStatusMessage.get_status_partially_admitted_non_saudi() or
             user.status_message == RegistrationStatusMessage.get_status_transfer())
            and AdmissionSemester.get_phase2_active_semester(user))


def is_admitted(user):
    phase = user.get_student_phase()
    return phase == 'ADMITTED'


def is_withdrawn(user):
    phase = user.get_student_phase()
    return phase == 'WITHDRAWN'


def is_eligible_to_withdraw(user):
    return user.status_message in [RegistrationStatusMessage.get_status_admitted(),
                                   RegistrationStatusMessage.get_status_admitted_final(),
                                   RegistrationStatusMessage.get_status_confirmed()]


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
        return can_confirm(self.request.user)


@login_required()
@user_passes_test(can_confirm)
def confirm(request):
    form = BaseAgreementForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            request.session['confirmed'] = True
            return redirect('undergraduate_admission:personal_info')
        else:
            messages.error(request, _('Error.'))

    sem = AdmissionSemester.get_phase2_active_semester(request.user)
    agreement = get_object_or_404(Agreement, agreement_type=Agreement.AgreementTypes.CONFIRMED_N, semester=sem)
    return render(request, 'undergraduate_admission/phase2/confirm.html', {'agreement': agreement,
                                                                           'form': form, })


@login_required()
@user_passes_test(can_confirm)
def personal_info(request):
    form = PersonalInfoForm(request.POST or None, request.FILES or None,
                            instance=request.user, )

    if request.method == 'GET':
        confirmed = request.session.get('confirmed')
        if confirmed is None:
            return redirect('undergraduate_admission:confirm')

    if request.method == 'POST':
        if form.is_valid():
            saved = form.save()
            if saved:
                messages.success(request, _('Personal Info was saved successfully...'))
                request.session['personal_info_completed'] = True
                return redirect('undergraduate_admission:guardian_contact')
            else:
                messages.error(request, _('Error saving info. Try again later!'))

    return render(request, 'undergraduate_admission/phase2/form-personal.html', {'form': form,
                                                                                 'step1': 'active'})


@login_required()
@user_passes_test(can_confirm)
def guardian_contact(request):
    if request.method == 'GET':
        personal_info_completed = request.session.get('personal_info_completed')
        if not personal_info_completed:
            return redirect('undergraduate_admission:personal_info')

    form = GuardianContactForm(request.POST or None, instance=request.user)

    if request.method == 'POST':
        if form.is_valid():
            saved = form.save()
            if saved:
                messages.success(request, _('Guardian Contact Info was saved successfully...'))
                request.session['guardian_contact_completed'] = True
                return redirect('undergraduate_admission:relative_contact')
            else:
                messages.error(request, _('Error saving info. Try again later!'))

    return render(request, 'undergraduate_admission/phase2/form.html', {'form': form,
                                                                        'step2': 'active'})


@login_required()
@user_passes_test(can_confirm)
def relative_contact(request):
    if request.method == 'GET':
        guardian_contact_completed = request.session.get('guardian_contact_completed')
        if not guardian_contact_completed:
            return redirect('undergraduate_admission:guardian_contact')

    form = RelativeContactForm(request.POST or None, instance=request.user)

    if request.method == 'POST':
        if form.is_valid():
            saved = form.save()
            if saved:
                messages.success(request, _('Relative Info was saved successfully...'))
                request.session['relative_contact_completed'] = True
                return redirect('undergraduate_admission:vehicle_info')
            else:
                messages.error(request, _('Error saving info. Try again later!'))

    return render(request, 'undergraduate_admission/phase2/form-relative.html', {'form': form,
                                                                                 'step3': 'active'})


@login_required()
@user_passes_test(can_confirm)
def vehicle_info(request):
    if request.method == 'GET':
        relative_contact_completed = request.session.get('relative_contact_completed')
        if not relative_contact_completed:
            return redirect('undergraduate_admission:relative_contact')

    form = VehicleInfoForm(request.POST or None, request.FILES or None, instance=request.user)

    if request.method == 'POST':
        if form.is_valid():
            saved = form.save()
            if saved:
                messages.success(request, _('Vehicle info was submitted successfully...'))
                request.session['vehicle_info_completed'] = True
                return redirect('undergraduate_admission:personal_picture')
            else:
                messages.error(request, _('Error saving info. Try again later!'))

    return render(request, 'undergraduate_admission/phase2/form-uploads.html', {'form': form,
                                                                                'step4': 'active'})


class PersonalPictureView(Phase2BaseView, UpdateView):
    template_name = 'undergraduate_admission/phase2/form-personal-picture.html'
    form_class = PersonalPhotoForm
    success_url = reverse_lazy('undergraduate_admission:personal_picture')

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
    success_url = reverse_lazy('undergraduate_admission:personal_picture_re_upload')

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


class UploadDocumentsView(Phase2BaseView, UpdateView):
    template_name = 'undergraduate_admission/phase2/form-uploads.html'
    form_class = DocumentsForm
    success_url = reverse_lazy('undergraduate_admission:student_area')

    def test_func(self):
        original_test_result = super(UploadDocumentsView, self).test_func()
        return original_test_result and self.request.GET.get('f', '')

    def get_context_data(self, **kwargs):
        context = super(UploadDocumentsView, self).get_context_data(**kwargs)
        context['step6'] = 'active'
        return context

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        if self.request.user.status_message == RegistrationStatusMessage.get_status_transfer():
            reg_msg = RegistrationStatusMessage.get_status_admitted_transfer_final()
        elif self.request.user.student_type == 'N':
            reg_msg = RegistrationStatusMessage.get_status_confirmed_non_saudi()
        else:
            reg_msg = RegistrationStatusMessage.get_status_confirmed()

        saved_user = form.save(commit=False)
        saved_user.status_message = reg_msg
        saved_user.save()

        if self.request.user.student_type in [RegistrationStatusMessage.get_status_confirmed_non_saudi(),
                                              RegistrationStatusMessage.get_status_confirmed()]:
            SMS.send_sms_confirmed(self.request.user.mobile)

        if saved_user:
            messages.success(self.request, _('Documents were uploaded successfully. We will verify your information '
                                             'and get back to you soon...'))
        else:
            messages.error(self.request, _('Error saving info. Try again later!'))

        return super(UploadDocumentsView, self).form_valid(form)


class UploadMissingDocumentsView(Phase2BaseView, UpdateView):
    template_name = 'undergraduate_admission/phase2/plain_form.html'
    form_class = MissingDocumentsForm
    success_url = reverse_lazy('undergraduate_admission:student_area')

    def test_func(self):
        original_test_result = super(UploadMissingDocumentsView, self).test_func()
        return original_test_result and self.request.user.verification_documents_incomplete

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        saved = form.save()
        if saved:
            messages.success(self.request, _('Documents were uploaded successfully. We will verify your information '
                                             'and get back to you soon...'))
        else:
            messages.error(self.request, _('Error saving info. Try again later!'))

        return super(UploadMissingDocumentsView, self).form_valid(form)


@login_required()
def upload_withdrawal_proof(request):
    # it is ok to come here unconditionally if student has duplicate admission in other universities
    if request.method == 'GET' and not request.user.status_message == RegistrationStatusMessage.get_status_duplicate():
        return redirect('undergraduate_admission:student_area')

    form = WithdrawalProofForm(request.POST or None, request.FILES or None, instance=request.user)

    if request.method == 'POST':
        if form.is_valid():
            saved = form.save()
            if saved:
                messages.success(request, _('Documents were uploaded successfully...'))
                request.session['upload_documents_completed'] = True
                return redirect('undergraduate_admission:student_area')
            else:
                messages.error(request, _('Error saving info. Try again later!'))

    return render(request, 'undergraduate_admission/phase2/plain_form.html', {'form': form, })


class WithdrawView(LoginRequiredMixin, SuccessMessageMixin, UserPassesTestMixin, UpdateView):
    template_name = 'undergraduate_admission/phase2/withdraw.html'
    form_class = WithdrawalForm
    success_url = reverse_lazy('undergraduate_admission:withdrawal_letter')
    success_message = _('You have withdrawn from the university successfully...')

    def test_func(self):
        return is_eligible_to_withdraw(self.request.user)

    def get_object(self, queryset=None):
        return self.request.user

    def get(self, request, *args, **kwargs):
        if request.method == "GET":
            if request.user.get_student_phase() == 'WITHDRAWN':
                return redirect("undergraduate_admission:withdrawal_letter")

        return super(WithdrawView, self).get(request, *args, **kwargs)

    # def form_valid(self, form):
    #     saved = form.save(commit=False)
    #     if saved:
    #         SMS.send_sms_withdrawn(self.object.mobile)
    #
    #         # added for housing module
    #         roommate_requests = RoommateRequest.objects.filter(requesting_user=self.object,
    #                                                            status__in=[
    #                                                                RoommateRequest.RequestStatuses.PENDING,
    #                                                                RoommateRequest.RequestStatuses.ACCEPTED])
    #         if roommate_requests.count() > 0:
    #             for roommate_request in roommate_requests:
    #                 SMS.send_sms_housing_roommate_request_withdrawn(roommate_request.requested_user.mobile)
    #             roommate_requests.update(status=RoommateRequest.RequestStatuses.REQUESTING_STUDENT_WITHDRAWN)
    #
    #         roommate_requests = RoommateRequest.objects.filter(requested_user=self.object,
    #                                                            status__in=[
    #                                                                RoommateRequest.RequestStatuses.PENDING,
    #                                                                RoommateRequest.RequestStatuses.ACCEPTED])
    #
    #         print(roommate_requests.count())
    #         if roommate_requests.count() > 0:
    #             for roommate_request in roommate_requests:
    #                 SMS.send_sms_housing_roommate_request_withdrawn(roommate_request.requesting_user.mobile)
    #             roommate_requests.update(status=RoommateRequest.RequestStatuses.REQUESTED_STUDENT_WITHDRAWN)
    #
    #     return super(WithdrawView, self).form_valid(form)


@login_required()
@user_passes_test(is_withdrawn)
def withdrawal_letter(request):
    if request.method == "GET" and request.user.get_student_phase() != 'WITHDRAWN':
        return redirect("undergraduate_admission:student_area")

    user = request.user

    return render(request, 'undergraduate_admission/phase2/letter_withdrawal.html', {'user': user, })


class TransferView(SuccessMessageMixin, FormView):
    template_name = 'undergraduate_admission/register.html'
    form_class = TransferForm
    success_url = reverse_lazy('undergraduate_admission:login')
    success_message = _('Your transfer request was approved')

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(TransferView, self).get_form_kwargs()
        kwargs['user'] = None
        return kwargs

    def form_valid(self, form):
        form.save()
        return super(TransferView, self).form_valid(form)
