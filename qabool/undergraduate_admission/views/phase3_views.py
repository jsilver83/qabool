from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView
from django.views.generic import TemplateView
from django.views.generic import UpdateView

from shared_app.base_views import StudentMixin
from undergraduate_admission.forms.phase1_forms import AgreementForm
from undergraduate_admission.forms.phase3_forms import TarifiTimeSlotForm
from undergraduate_admission.models import AdmissionSemester, Agreement, RegistrationStatus, KFUPMIDsPool


class Phase3BaseView(StudentMixin):
    def test_func(self):
        super_test_result = super().test_func()
        return super_test_result and self.admission_request.can_access_phase3()


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
        sem = AdmissionSemester.get_phase3_active_semester(self.admission_request)
        context['agreement'] = get_object_or_404(Agreement, agreement_type=self.agreement_type,
                                                 status_message=self.admission_request.status_message,
                                                 semester=sem)
        context[self.step_number] = 'active'
        return context

    def form_valid(self, form):
        self.request.session[self.step_number] = True
        return redirect(self.next_url)

    def form_invalid(self, form):
        messages.error(self.request, _('Error.'))
        return super(BaseStudentAgreement, self).form_invalid(form)


class StudentAgreement1(BaseStudentAgreement):
    agreement_type = Agreement.AgreementTypes.STUDENT_AGREEMENT_1
    step_number = 'step1'
    next_url = 'undergraduate_admission:student_agreement_2'


class StudentAgreement2(BaseStudentAgreement):
    agreement_type = Agreement.AgreementTypes.STUDENT_AGREEMENT_4
    check_step = 'step1'
    step_number = 'step2'
    next_url = 'undergraduate_admission:student_agreement_3'


class StudentAgreement3(BaseStudentAgreement):
    agreement_type = Agreement.AgreementTypes.STUDENT_AGREEMENT_2
    check_step = 'step2'
    step_number = 'step3'
    next_url = 'undergraduate_admission:student_agreement_4'


class StudentAgreement4(BaseStudentAgreement):
    agreement_type = Agreement.AgreementTypes.STUDENT_AGREEMENT_3
    check_step = 'step3'
    step_number = 'step4'
    next_url = 'undergraduate_admission:choose_tarifi_time_slot'


class ChooseTarifiTimeSlot(Phase3BaseView, UpdateView):
    form_class = TarifiTimeSlotForm
    template_name = 'undergraduate_admission/phase3/tarifi_time_slot.html'
    success_url = reverse_lazy('undergraduate_admission:print_documents')

    def get_context_data(self, **kwargs):
        context = super(ChooseTarifiTimeSlot, self).get_context_data(**kwargs)
        sem = AdmissionSemester.get_active_semester()
        context['agreement'] = get_object_or_404(Agreement,
                                                 status_message=self.admission_request.status_message,
                                                 agreement_type=Agreement.AgreementTypes.AWARENESS_WEEK_AGREEMENT,
                                                 semester=sem)

        return context

    def get_object(self, queryset=None):
        return self.admission_request

    def form_valid(self, form):
        saved = form.save(commit=False)
        saved.phase3_submit_date = timezone.now()
        # if self.request.user.student_type in ['S', 'M']:
        kfupm_id = KFUPMIDsPool.get_next_available_id(self.admission_request)

        if kfupm_id:
            if not saved.kfupm_id:
                saved.kfupm_id = kfupm_id
        else:
            messages.error(self.request, _('No IDs to assign. Contact the site admins...'))
            return redirect('undergraduate_admission:student_area')

        messages.success(self.request, _('Tarifi time slot was chosen successfully...'))

        return super(ChooseTarifiTimeSlot, self).form_valid(form)


class AdmissionLetters(Phase3BaseView, TemplateView):
    template_name = 'undergraduate_admission/phase3/letter_admission.html'

    def test_func(self):
        return super().test_func() or self.admission_request.tarifi_week_attendance_date

    def dispatch(self, request, *args, **kwargs):
        self.init_class_variables(self.request, *args, **kwargs)
        if not self.admission_request.admission_letter_print_date:
            self.admission_request.admission_letter_print_date = timezone.now()
        if not self.admission_request.medical_report_print_date:
            self.admission_request.medical_report_print_date = timezone.now()

        if self.admission_request.status_message in [RegistrationStatus.get_status_admitted_final(),
                                                     RegistrationStatus.get_status_admitted_transfer_final(),
                                                     RegistrationStatus.get_status_admitted_non_saudi_final()]:
            pass

        else:
            if (self.admission_request.student_type in ['S', 'M']
                    and self.admission_request.status_message == RegistrationStatus.get_status_admitted()):
                status = RegistrationStatus.get_status_admitted_final()
            elif self.admission_request.status_message == RegistrationStatus.get_status_admitted_transfer():
                status = RegistrationStatus.get_status_admitted_transfer_final()
            else:
                status = RegistrationStatus.get_status_admitted_non_saudi_final()

            self.admission_request.status_message = status
            self.admission_request.save()

        return super(AdmissionLetters, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(AdmissionLetters, self).get_context_data(**kwargs)
        context['user'] = self.admission_request
        context['show_admission_letter'] = self.admission_request.can_print_admission_letter()
        context['show_medical_report'] = self.admission_request.can_print_medical_report()

        return context
