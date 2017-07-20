from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView
from django.views.generic import TemplateView
from django.views.generic import UpdateView

from undergraduate_admission.forms.phase1_forms import AgreementForm
from undergraduate_admission.forms.phase3_forms import TarifiTimeSlotForm, ChooseRoommateForm
from undergraduate_admission.models import AdmissionSemester, Agreement, RegistrationStatusMessage, KFUPMIDsPool
from undergraduate_admission.utils import SMS


class Phase3BaseView(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.status_message == RegistrationStatusMessage.get_status_admitted() \
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
    agreement_type = 'STUDENT_AGREEMENT_3'
    check_step = 'step2'
    step_number = 'step3'
    next_url = 'student_agreement_4'


class StudentAgreement4(BaseStudentAgreement):
    agreement_type = 'STUDENT_AGREEMENT_2'
    check_step = 'step3'
    step_number = 'step4'
    next_url = 'choose_tarifi_time_slot'


class ChooseTarifiTimeSlot(Phase3BaseView, UpdateView):
    form_class = TarifiTimeSlotForm
    template_name = 'undergraduate_admission/phase3/tarifi_time_slot.html'
    success_url = 'print_documents'

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        kfupm_id = KFUPMIDsPool.get_next_available_id()

        if kfupm_id:
            saved = form.save(commit=False)
            saved.phase3_submit_date = timezone.now()
            if not saved.kfupm_id:
                saved.kfupm_id = kfupm_id
            saved.save()

            if saved:
                messages.success(self.request, _('Tarifi time slot was chosen successfully...'))
                return redirect(self.success_url)
        else:
            messages.error(self.request, _('No IDs to assign. Contact the site admins...'))
            return redirect('student_area')


class PrintDocuments(Phase3BaseView, TemplateView):
    template_name = 'undergraduate_admission/phase3/print_documents.html'


class BasePrintDocuments(Phase3BaseView, TemplateView):
    template_name = 'undergraduate_admission/phase3/print_documents_no_steps.html'

    def test_func(self):
        return self.request.user.status_message == RegistrationStatusMessage.get_status_admitted() \
           and self.request.user.tarifi_week_attendance_date


class AdmissionLetter(BasePrintDocuments):
    template_name = 'undergraduate_admission/phase3/letter_admission.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.admission_letter_print_date:
            request.user.admission_letter_print_date = timezone.now()
            request.user.save()
        return super(AdmissionLetter, self).dispatch(request, *args, **kwargs)


class MedicalLetter(BasePrintDocuments):
    template_name = 'undergraduate_admission/phase3/letter_medical.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.medical_report_print_date:
            request.user.medical_report_print_date = timezone.now()
            request.user.save()
        return super(MedicalLetter, self).dispatch(request, *args, **kwargs)
