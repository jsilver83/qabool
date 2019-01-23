from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import UpdateView, FormView, TemplateView

from shared_app.base_views import StudentMixin
from undergraduate_admission.forms.general_forms import MyAuthenticationForm, ForgotPasswordForm, BaseContactForm
from undergraduate_admission.models import AdmissionSemester, RegistrationStatusMessage


class IndexView(FormView):
    template_name = 'undergraduate_admission/login.html'
    form_class = MyAuthenticationForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('undergraduate_admission:student_area')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['next'] = self.request.POST.get(
            'next', self.request.GET.get('next', reverse_lazy('undergraduate_admission:student_area'))
        )
        context['phase1_active'] = False
        if AdmissionSemester.check_if_phase1_is_active():
            context['phase1_active'] = True
        return context

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(self.request, user)
                return redirect(self.get_context_data().get('next'))
        return super().form_valid(form)


def forgot_password(request):
    form = ForgotPasswordForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            saved = form.save()
            if saved:
                messages.success(request, _('Password was reset successfully...'))
                return redirect('undergraduate_admission:index')
            else:
                messages.error(request, _('Error resetting password. Make sure you enter the correct info.'))

    return render(request, 'undergraduate_admission/forgot_password.html', {'form': form})


class StudentArea(StudentMixin, TemplateView):
    template_name = 'undergraduate_admission/student_area.html'

    def get_context_data(self, **kwargs):
        context = super(StudentArea, self).get_context_data(**kwargs)
        # TODO: fix and make it unified in business logic
        phase = self.admission_request.get_student_phase()

        status_message = self.admission_request.status_message

        show_result = phase in ['PARTIALLY-ADMITTED', 'REJECTED']

        can_confirm = ((
                                   self.admission_request.status_message == RegistrationStatusMessage.get_status_partially_admitted() or
                                   self.admission_request.status_message == RegistrationStatusMessage.get_status_transfer())
                       and AdmissionSemester.get_phase2_active_semester(self.admission_request.user))

        can_finish_phase3 = self.admission_request.status_message in [RegistrationStatusMessage.get_status_admitted(),
                                                                      RegistrationStatusMessage.get_status_admitted_non_saudi()] \
                            and not self.admission_request.tarifi_week_attendance_date \
                            and AdmissionSemester.get_phase3_active_semester(self.admission_request.user)

        can_re_upload_docs = phase == ('PARTIALLY-ADMITTED'
                                       and self.admission_request.verification_documents_incomplete)

        can_re_upload_picture = phase == ('PARTIALLY-ADMITTED'
                                          and self.admission_request.verification_picture_acceptable)

        can_upload_withdrawal_proof = status_message == RegistrationStatusMessage.get_status_duplicate()

        context['user'] = self.admission_request
        context['show_result'] = show_result
        context['can_confirm'] = can_confirm
        context['can_re_upload_docs'] = can_re_upload_docs
        context['can_re_upload_picture'] = can_re_upload_picture
        context['can_upload_withdrawal_proof'] = can_upload_withdrawal_proof
        context['can_finish_phase3'] = can_finish_phase3

        return context


class EditContactInfo(StudentMixin, SuccessMessageMixin, UpdateView):
    template_name = 'undergraduate_admission/edit_contact_info.html'
    form_class = BaseContactForm
    success_message = _('Contact Info was updated successfully...')
    success_url = reverse_lazy('undergraduate_admission:student_area')

    def get_object(self, queryset=None):
        return self.admission_request

    def get_form_kwargs(self):
        kwargs = super(EditContactInfo, self).get_form_kwargs()
        kwargs['request'] = self.request

        return kwargs


def csrf_failure(request, reason=""):
    return render(request, 'undergraduate_admission/csrf_failure.html')
