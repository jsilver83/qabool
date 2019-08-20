from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import UpdateView, FormView, TemplateView

from shared_app.base_views import StudentMixin
from undergraduate_admission.forms.general_forms import MyAuthenticationForm, ForgotPasswordForm, BaseContactForm
from undergraduate_admission.models import AdmissionSemester, RegistrationStatus, VerificationIssues


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


class ForgotPassword(SuccessMessageMixin, FormView):
    template_name = 'undergraduate_admission/forgot_password.html'
    form_class = ForgotPasswordForm
    success_url = reverse_lazy('undergraduate_admission:index')
    success_message = _('Password was reset successfully...')

    def form_valid(self, form):
        saved = form.save()

        return super().form_valid(form)


class StudentArea(StudentMixin, TemplateView):
    template_name = 'undergraduate_admission/student_area.html'

    def get_context_data(self, **kwargs):
        context = super(StudentArea, self).get_context_data(**kwargs)
        context['admission_request'] = self.admission_request

        try:
            from tarifi.views import allowed_statuses_for_tarifi_week
            if self.admission_request.status_message in allowed_statuses_for_tarifi_week:
                context['tarifi_data'] = getattr(self.admission_request, 'tarifi_data', None)
        except:
            pass

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
