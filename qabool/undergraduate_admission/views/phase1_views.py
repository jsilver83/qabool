from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_protect
from django.views.generic import CreateView, TemplateView, UpdateView

from shared_app.base_views import StudentMixin
from undergraduate_admission.forms.phase1_forms import AgreementForm, RegistrationForm, Phase1UserEditForm
from undergraduate_admission.utils import SMS, Email
from ..models import *

User = get_user_model()


@cache_page(60 * 15)
@csrf_protect
def initial_agreement(request):
    form = AgreementForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            request.session['agreed'] = True
            return redirect('undergraduate_admission:register')
        else:
            messages.error(request, _('Error.'))
    sem = AdmissionSemester.get_phase1_active_semester()
    agreement = get_object_or_404(Agreement, agreement_type=Agreement.AgreementTypes.INITIAL, semester=sem)
    return render(request, 'undergraduate_admission/agreement.html', {'agreement': agreement,
                                                                      'form': form, })


class RegisterView(CreateView):
    model = AdmissionRequest
    context_object_name = "user"
    template_name = 'undergraduate_admission/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('undergraduate_admission:registration_success')

    # changed from "dispatch" to "get" so that it will check only when the user loads the form not when he submits
    def get(self, request, *args, **kwargs):
        if not AdmissionSemester.check_if_phase1_is_active():
            messages.error(request, _('Registration is closed...'))
            return redirect('undergraduate_admission:index')

        agreed = request.session.get('agreed')
        if agreed is None:
            return redirect('undergraduate_admission:initial_agreement')
        else:
            return super(RegisterView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        semester = AdmissionSemester.get_phase1_active_semester()
        context['non_saudi_agreement'] = Agreement.objects.filter(
            agreement_type=Agreement.AgreementTypes.INITIAL,
            status_message=RegistrationStatus.get_status_applied_non_saudi(),
            semester=semester,
        ).first()

        return context

    def form_valid(self, form):
        user_exists_before = User.objects.filter(username=form.cleaned_data['username']).exists()
        if user_exists_before:
            user = User.objects.get(username=form.cleaned_data['username'])
        else:
            user = User.objects.create_user(username=form.cleaned_data['username'],
                                            password=form.cleaned_data['password1'],
                                            email=form.cleaned_data['email'])

        semester = AdmissionSemester.get_phase1_active_semester()
        if user.admission_requests.filter(semester=semester).exists():
            messages.error(self.request, _('You already registered for this year.'))
            return redirect('undergraduate_admission:index')
        else:
            if user_exists_before:
                # if the user was created in the past and that user is applying again, it makes sense to change the
                # existing old user and update it with the new credentials and email
                user.email = form.cleaned_data['email']
                user.set_password(form.cleaned_data['password1'])
                user.save()

            reg_msg = RegistrationStatus.get_status_applied()
            non_saudi_reg_msg = RegistrationStatus.get_status_applied_non_saudi()
            old_high_school_reg_msg = RegistrationStatus.get_status_old_high_school()

            student = AdmissionRequest(
                # first_name_ar=form.cleaned_data.get('first_name_ar'),
                # second_name_ar=form.cleaned_data.get('second_name_ar'),
                # third_name_ar=form.cleaned_data.get('third_name_ar'),
                # family_name_ar=form.cleaned_data.get('family_name_ar'),
                # first_name_en=form.cleaned_data.get('first_name_en'),
                # second_name_en=form.cleaned_data.get('second_name_en'),
                # third_name_en=form.cleaned_data.get('third_name_en'),
                # family_name_en=form.cleaned_data.get('family_name_en'),
                student_full_name_ar=form.cleaned_data['student_full_name_ar'],
                student_full_name_en=form.cleaned_data['student_full_name_en'],
                semester=semester,
                nationality=form.cleaned_data['nationality'],
                saudi_mother=form.cleaned_data['saudi_mother'],
                saudi_mother_gov_id=form.cleaned_data['saudi_mother_gov_id'],
                mobile=form.cleaned_data['mobile'],
                guardian_mobile=form.cleaned_data['guardian_mobile'],
                high_school_graduation_year=form.cleaned_data['high_school_graduation_year'],
                high_school_gpa_student_entry=form.cleaned_data['high_school_gpa_student_entry'],
                high_school_system=form.cleaned_data['high_school_system'],
                high_school_certificate=form.cleaned_data['high_school_certificate'],
                courses_certificate=form.cleaned_data['courses_certificate'],
                student_notes=form.cleaned_data['student_notes'],
                user=user,
            )

            if form.cleaned_data['high_school_graduation_year'].type == GraduationYear.GraduationYearTypes.OLD_HS:
                student.status_message = old_high_school_reg_msg
                student.save()
                SMS.send_sms_registration_success_old_high_school(student.mobile)
                SMS.send_sms_registration_success_old_high_school(student.guardian_mobile)
            elif form.cleaned_data["nationality"] != 'SA' and not form.cleaned_data["saudi_mother"]:
                student.status_message = non_saudi_reg_msg
                student.save()
                SMS.send_sms_registration_success(student.mobile)
                SMS.send_sms_registration_success(student.guardian_mobile)
            else:
                student.status_message = reg_msg
                student.save()
                SMS.send_sms_registration_success(student.mobile)
                SMS.send_sms_registration_success(student.guardian_mobile)

            Email.send_email_registration_success(student)

            self.request.session['admission_request'] = student.id

        return redirect(self.success_url)


class RegistrationSuccess(TemplateView):
    template_name = 'undergraduate_admission/registration_success.html'

    def get_context_data(self, **kwargs):
        context = super(RegistrationSuccess, self).get_context_data(**kwargs)
        admission_request_id = self.request.session.get('admission_request', -1)
        admission_request = get_object_or_404(AdmissionRequest, pk=admission_request_id)
        if admission_request is not None:
            context['admission_request'] = admission_request
        else:
            return redirect('undergraduate_admission:register')

        return context


class EditInfo(StudentMixin, SuccessMessageMixin, UpdateView):
    template_name = 'undergraduate_admission/edit_info.html'
    form_class = Phase1UserEditForm
    success_message = _('Info was updated successfully...')
    success_url = reverse_lazy('undergraduate_admission:student_area')

    def get_object(self, queryset=None):
        return self.admission_request

    def get_form_kwargs(self):
        kwargs = super(EditInfo, self).get_form_kwargs()
        kwargs['request'] = self.request

        return kwargs
