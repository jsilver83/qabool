from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView
from django.views.generic import TemplateView
from django.views.generic import UpdateView

from undergraduate_admission.forms.phase1_forms import AgreementForm
from undergraduate_admission.forms.phase3_forms import TarifiTimeSlotForm
from undergraduate_admission.models import AdmissionSemester, Agreement, RegistrationStatusMessage, KFUPMIDsPool
from undergraduate_admission.utils import SMS


class Phase3BaseView(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.status_message in [RegistrationStatusMessage.get_status_admitted(),
                                                    RegistrationStatusMessage.get_status_admitted_non_saudi()] \
           and AdmissionSemester.get_phase3_active_semester(self.request.user)


class BaseStudentAgreement(Phase3BaseView, FormView):
    template_name = 'undergraduate_admission/phase2/student_agreement.html'
    form_class = AgreementForm
    agreement_type = 'n/a'
    check_step = ''
    step_number = 'n/a'
    next_url = 'n/a'

    def test_func(self):
        test_result = super(BaseStudentAgreement, self).test_func()
        if self.check_step:
            return self.request.session.get(self.check_step) and test_result
        else:
            return test_result

    def get_context_data(self, **kwargs):
        context = super(BaseStudentAgreement, self).get_context_data(**kwargs)
        sem = AdmissionSemester.get_phase3_active_semester(self.request.user)
        context['agreement'] = get_object_or_404(Agreement, agreement_type=self.agreement_type, semester=sem)
        context['items'] = context['agreement'].items.filter(show=True)
        context[self.step_number] = 'active'
        return context

    def form_valid(self, form):
        self.request.session[self.step_number] = True
        return redirect(self.next_url)

    def form_invalid(self, form):
        messages.error(self.request, _('Error.'))
        return super(BaseStudentAgreement, self).form_invalid(form)


class StudentAgreement1(BaseStudentAgreement):
    agreement_type = 'STUDENT_AGREEMENT_1'
    step_number = 'step1'
    next_url = 'student_agreement_2'


class StudentAgreement2(BaseStudentAgreement):
    agreement_type = 'STUDENT_AGREEMENT_4'
    check_step = 'step1'
    step_number = 'step2'
    next_url = 'student_agreement_3'


class StudentAgreement3(BaseStudentAgreement):
    agreement_type = 'STUDENT_AGREEMENT_2'
    check_step = 'step2'
    step_number = 'step3'
    next_url = 'student_agreement_4'


class StudentAgreement4(BaseStudentAgreement):
    agreement_type = 'STUDENT_AGREEMENT_3'
    check_step = 'step3'
    step_number = 'step4'
    next_url = 'choose_tarifi_time_slot'


class ChooseTarifiTimeSlot(Phase3BaseView, UpdateView):
    form_class = TarifiTimeSlotForm
    template_name = 'undergraduate_admission/phase3/tarifi_time_slot.html'
    success_url = reverse_lazy('undergraduate_admission:print_documents')

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.status_message == RegistrationStatusMessage.get_status_admitted_transfer_final():
            return redirect('student_area')
        else:
            return super(ChooseTarifiTimeSlot, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ChooseTarifiTimeSlot, self).get_context_data(**kwargs)
        sem = AdmissionSemester.get_active_semester()
        context['agreement'] = get_object_or_404(Agreement, agreement_type='AWARENESS_WEEK_AGREEMENT', semester=sem)
        context['items'] = context['agreement'].items.filter(show=True)

        return context

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        saved = form.save(commit=False)
        saved.phase3_submit_date = timezone.now()

        # if self.request.user.student_type in ['S', 'M']:
        kfupm_id = KFUPMIDsPool.get_next_available_id(self.request.user)

        if kfupm_id:
            if not saved.kfupm_id:
                saved.kfupm_id = kfupm_id
        else:
            messages.error(self.request, _('No IDs to assign. Contact the site admins...'))
            return redirect('student_area')

        messages.success(self.request, _('Tarifi time slot was chosen successfully...'))

        return super(ChooseTarifiTimeSlot, self).form_valid(form)


class AdmissionLetters(Phase3BaseView, TemplateView):
    template_name = 'undergraduate_admission/phase3/letter_admission.html'

    def test_func(self):
        return self.request.user.status_message in [RegistrationStatusMessage.get_status_admitted_final(),
                                                    RegistrationStatusMessage.get_status_admitted_final_non_saudi()] \
           and (AdmissionSemester.get_phase3_active_semester(self.request.user)
                or self.request.user.tarifi_week_attendance_date)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.admission_letter_print_date:
            request.user.admission_letter_print_date = timezone.now()
        if not request.user.medical_report_print_date:
            request.user.medical_report_print_date = timezone.now()

        if self.request.user.student_type in ['S', 'M']:
            status = RegistrationStatusMessage.get_status_admitted_final()
        else:
            status = RegistrationStatusMessage.get_status_admitted_final_non_saudi()

        request.user.status_message = status
        request.user.save()

        return super(AdmissionLetters, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(AdmissionLetters, self).get_context_data(**kwargs)
        context['show_admission_letter'] = self.request.user.student_type in ['S', 'M']

        return context
