from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.generic import UpdateView, FormView
from django.views.generic.base import View, TemplateView
from sendfile import sendfile

from find_roommate.models import RoommateRequest
from shared_app.base_views import StudentMixin
from shared_app.utils import get_current_admission_request_for_logged_in_user
from undergraduate_admission.forms.phase1_forms import BaseAgreementForm
from undergraduate_admission.forms.phase2_forms import PersonalInfoForm, DocumentsForm, GuardianContactForm, \
    RelativeContactForm, WithdrawalForm, WithdrawalProofForm, PersonalPhotoForm, TransferForm, \
    MissingDocumentsForm
from undergraduate_admission.models import AdmissionSemester, Agreement, RegistrationStatus, AdmissionRequest
from undergraduate_admission.utils import SMS


@method_decorator(never_cache, name='dispatch')
class UserFileView(LoginRequiredMixin, UserPassesTestMixin, View):
    raise_exception = True  # PermissionDenied
    admission_request = None

    def dispatch(self, request, *args, **kwargs):
        self.admission_request = get_current_admission_request_for_logged_in_user(request)
        if self.admission_request is None:
            self.admission_request = get_object_or_404(AdmissionRequest, pk=self.kwargs['pk'])

        return super().dispatch(request, *args, **kwargs)

    def test_func(self):
        return self.request.user.is_staff or self.admission_request.id == int(self.kwargs['pk'])\
               or self.admission_request.can_search_in_housing()

    def get(self, request, filetype, pk):
        try:
            user_file = getattr(self.admission_request, filetype)
        except AttributeError:  # invalid filetype
            raise Http404
        if not user_file:  # file not uploaded
            raise Http404
        return sendfile(request, user_file.path)


class Phase2BaseView(StudentMixin):
    def test_func(self):
        return super(Phase2BaseView, self).test_func() and self.admission_request.can_confirm()


class Confirm(Phase2BaseView, FormView):
    form_class = BaseAgreementForm
    template_name = 'undergraduate_admission/phase2/confirm.html'
    success_url = reverse_lazy('undergraduate_admission:personal_info')

    def form_valid(self, form):
        self.request.session['confirmed'] = True
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sem = AdmissionSemester.get_phase2_active_semester(self.admission_request)
        context['agreement'] = get_object_or_404(Agreement,
                                                 agreement_type=Agreement.AgreementTypes.CONFIRM,
                                                 status_message=self.admission_request.status_message,
                                                 semester=sem)
        return context


class BaseStudentInfoUpdateView(SuccessMessageMixin, StudentMixin, UpdateView):
    form_class = None
    success_message = None
    template_name = None
    success_url = None
    required_session_variable = 'dumb'
    affected_session_variable = 'and_dumber_to'
    previous_step_url = None
    current_step_no = None

    def get(self, request, *args, **kwargs):
        if self.required_session_variable and request.session.get(self.required_session_variable) is None:
            return redirect(self.previous_step_url)
        return super().get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.admission_request

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[self.current_step_no] = 'active'
        return context

    def form_valid(self, form):
        if self.affected_session_variable:
            self.request.session[self.affected_session_variable] = True
        return super().form_valid(form)


class PersonalInfoView(BaseStudentInfoUpdateView):
    form_class = PersonalInfoForm
    success_message = _('Personal Info was saved successfully...')
    template_name = 'undergraduate_admission/phase2/form-personal.html'
    success_url = reverse_lazy('undergraduate_admission:guardian_contact')
    required_session_variable = 'confirmed'
    affected_session_variable = 'personal_info_completed'
    previous_step_url = reverse_lazy('undergraduate_admission:confirm')
    current_step_no = 'step1'


class GuardianContactView(BaseStudentInfoUpdateView):
    form_class = GuardianContactForm
    success_message = _('Guardian Contact Info was saved successfully...')
    template_name = 'undergraduate_admission/phase2/form.html'
    success_url = reverse_lazy('undergraduate_admission:relative_contact')
    required_session_variable = 'personal_info_completed'
    affected_session_variable = 'guardian_contact_completed'
    previous_step_url = reverse_lazy('undergraduate_admission:personal_info')
    current_step_no = 'step2'


class RelativeContactView(BaseStudentInfoUpdateView):
    form_class = RelativeContactForm
    success_message = _('Relative Info was saved successfully...')
    template_name = 'undergraduate_admission/phase2/form-relative.html'
    success_url = reverse_lazy('undergraduate_admission:personal_picture')
    required_session_variable = 'guardian_contact_completed'
    affected_session_variable = 'relative_contact_completed'
    previous_step_url = reverse_lazy('undergraduate_admission:guardian_contact')
    current_step_no = 'step3'


class PersonalPictureView(BaseStudentInfoUpdateView):
    form_class = PersonalPhotoForm
    success_message = _('Personal picture was uploaded successfully...')
    template_name = 'undergraduate_admission/phase2/form-personal-picture.html'
    success_url = reverse_lazy('undergraduate_admission:personal_picture')
    required_session_variable = 'relative_contact_completed'
    affected_session_variable = 'personal_picture_completed'
    previous_step_url = reverse_lazy('undergraduate_admission:relative_contact')
    current_step_no = 'step4'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['base_extend'] = 'undergraduate_admission/phase2/form.html'
        context['re_upload'] = False
        return context


class PersonalPictureUnacceptableView(BaseStudentInfoUpdateView):
    form_class = PersonalPhotoForm
    success_message = _('Personal picture was uploaded successfully...')
    template_name = 'undergraduate_admission/phase2/form-personal-picture.html'
    success_url = reverse_lazy('undergraduate_admission:student_area')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['base_extend'] = 'base_student_area.html'
        context['re_upload'] = True
        return context


class UploadDocumentsView(BaseStudentInfoUpdateView):
    form_class = DocumentsForm
    success_message = _('Documents were uploaded successfully. We will verify your information and get back to '
                        'you soon...')
    template_name = 'undergraduate_admission/phase2/form-uploads.html'
    success_url = reverse_lazy('undergraduate_admission:student_area')
    required_session_variable = ''
    affected_session_variable = 'personal_picture_completed'
    previous_step_url = reverse_lazy('undergraduate_admission:personal_picture')
    current_step_no = 'step5'

    def form_valid(self, form):
        if self.admission_request.status_message == RegistrationStatus.get_status_transfer():
            reg_msg = RegistrationStatus.get_status_admitted_transfer_final()
        elif self.admission_request.student_type == 'N':
            reg_msg = RegistrationStatus.get_status_confirmed_non_saudi()
        else:
            reg_msg = RegistrationStatus.get_status_confirmed()

        saved_user = form.save(commit=False)
        saved_user.status_message = reg_msg
        saved_user.save()

        if self.admission_request.status_message in [RegistrationStatus.get_status_confirmed_non_saudi(),
                                                     RegistrationStatus.get_status_confirmed()]:
            SMS.send_sms_confirmed(self.admission_request.mobile)

        if saved_user:
            messages.success(self.request, self.success_message)
        else:
            messages.error(self.request, _('Error saving info. Try again later!'))

        return super().form_valid(form)


class UploadMissingDocumentsView(Phase2BaseView, UpdateView):
    template_name = 'undergraduate_admission/phase2/plain_form.html'
    form_class = MissingDocumentsForm
    success_url = reverse_lazy('undergraduate_admission:student_area')

    def test_func(self):
        original_test_result = super(UploadMissingDocumentsView, self).test_func()
        return original_test_result and self.get_object().can_re_upload_docs

    def get_object(self):
        return self.admission_request

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
    if request.method == 'GET' and not request.user.status_message == RegistrationStatus.get_status_duplicate():
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


class WithdrawView(StudentMixin, SuccessMessageMixin, UpdateView):
    template_name = 'undergraduate_admission/phase2/withdraw.html'
    form_class = WithdrawalForm
    success_url = reverse_lazy('undergraduate_admission:withdrawal_letter')
    success_message = _('You have withdrawn from the university successfully...')

    def test_func(self):
        super_test_result = super().test_func()
        return super_test_result and self.admission_request.can_withdraw()

    def get_object(self, queryset=None):
        return self.admission_request

    def get(self, request, *args, **kwargs):
        if self.admission_request.can_print_withdrawal_letter():
            return redirect("undergraduate_admission:withdrawal_letter")

        return super(WithdrawView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        saved = form.save(commit=False)
        if saved:
            SMS.send_sms_withdrawn(self.object.mobile)

            # added for housing module
            roommate_requests = RoommateRequest.objects.filter(requesting_user=self.object,
                                                               status__in=[
                                                                   RoommateRequest.RequestStatuses.PENDING,
                                                                   RoommateRequest.RequestStatuses.ACCEPTED])
            if roommate_requests.count() > 0:
                for roommate_request in roommate_requests:
                    SMS.send_sms_housing_roommate_request_withdrawn(roommate_request.requested_user.mobile)
                roommate_requests.update(status=RoommateRequest.RequestStatuses.REQUESTING_STUDENT_WITHDRAWN)

            roommate_requests = RoommateRequest.objects.filter(requested_user=self.object,
                                                               status__in=[
                                                                   RoommateRequest.RequestStatuses.PENDING,
                                                                   RoommateRequest.RequestStatuses.ACCEPTED])

            if roommate_requests.count() > 0:
                for roommate_request in roommate_requests:
                    SMS.send_sms_housing_roommate_request_withdrawn(roommate_request.requesting_user.mobile)
                roommate_requests.update(status=RoommateRequest.RequestStatuses.REQUESTED_STUDENT_WITHDRAWN)

        return super(WithdrawView, self).form_valid(form)


class WithdrawalLetterView(StudentMixin, TemplateView):
    template_name = 'undergraduate_admission/phase2/letter_withdrawal.html'

    def test_func(self):
        super_test_result = super().test_func()
        return super_test_result and self.admission_request.can_print_withdrawal_letter()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.admission_request

        return context


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
