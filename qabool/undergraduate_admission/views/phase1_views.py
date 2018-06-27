from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import redirect, get_object_or_404, render
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_protect
from django.views.generic import CreateView, TemplateView, UpdateView
from django.utils.translation import ugettext_lazy as _
from django.core.cache import cache

from undergraduate_admission.filters import UserListFilter
from undergraduate_admission.forms.phase1_forms import AgreementForm, RegistrationForm, Phase1UserEditForm
from undergraduate_admission.models import User, RegistrationStatusMessage, AdmissionSemester, Agreement, \
    ImportantDateSidebar, GraduationYear
from undergraduate_admission.utils import SMS, Email, try_parse_float


@cache_page(60 * 15)
@csrf_protect
def initial_agreement(request):
    form = AgreementForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            request.session['agreed'] = True
            return redirect('register')
        else:
            messages.error(request, _('Error.'))
    sem = AdmissionSemester.get_phase1_active_semester()
    agreement = get_object_or_404(Agreement, agreement_type='INITIAL', semester=sem)
    agreement_items = agreement.items.filter(show=True)
    return render(request, 'undergraduate_admission/agreement.html', {'agreement': agreement,
                                                                      'items': agreement_items,
                                                                      'form': form, })


class RegisterView(CreateView):
    model = User
    context_object_name = "user"
    template_name = 'undergraduate_admission/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('registration_success')

    # changed from "dispatch" to "get" so that it will check only when the user loads the form not when he submits
    def get(self, request, *args, **kwargs):
        if not AdmissionSemester.check_if_phase1_is_active():
            messages.error(request, _('Registration is closed...'))
            return redirect('index')

        agreed = request.session.get('agreed')
        if agreed is None:
            return redirect('initial_agreement')
        else:
            return super(RegisterView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        # reg_msg = RegistrationStatusMessage.objects.get(pk=1) # for status 1 'application submitted'
        reg_msg = RegistrationStatusMessage.get_status_applied()
        non_saudi_reg_msg = RegistrationStatusMessage.get_status_non_saudi()
        old_high_school_reg_msg = RegistrationStatusMessage.get_status_old_high_school()
        semester = AdmissionSemester.get_phase1_active_semester()

        if form.cleaned_data['high_school_graduation_year'].type == GraduationYear.GraduationYearTypes.OLD_HS:
            user = User.objects.create_user(form.cleaned_data['username'],
                                            form.cleaned_data['email'],
                                            form.cleaned_data['password1'],
                                            first_name_ar=form.cleaned_data.get('first_name_ar'),
                                            second_name_ar=form.cleaned_data.get('second_name_ar'),
                                            third_name_ar=form.cleaned_data.get('third_name_ar'),
                                            family_name_ar=form.cleaned_data.get('family_name_ar'),
                                            first_name_en=form.cleaned_data.get('first_name_en'),
                                            second_name_en=form.cleaned_data.get('second_name_en'),
                                            third_name_en=form.cleaned_data.get('third_name_en'),
                                            family_name_en=form.cleaned_data.get('family_name_en'),
                                            high_school_graduation_year=form.cleaned_data['high_school_graduation_year'],
                                            status_message=old_high_school_reg_msg,
                                            semester=semester,
                                            nationality=form.cleaned_data['nationality'],
                                            saudi_mother=form.cleaned_data['saudi_mother'],
                                            saudi_mother_gov_id = form.cleaned_data['saudi_mother_gov_id'],
                                            mobile=form.cleaned_data['mobile'],
                                            guardian_mobile=form.cleaned_data['guardian_mobile'],
                                            high_school_gpa_student_entry=
                                            form.cleaned_data['high_school_gpa_student_entry'],
                                            student_notes=form.cleaned_data['student_notes'],
                                            high_school_system=form.cleaned_data['high_school_system'],
                                            )
            SMS.send_sms_registration_success_old_high_school(user.mobile)
            SMS.send_sms_registration_success_old_high_school(user.guardian_mobile)
        elif form.cleaned_data["nationality"].nationality_en != 'Saudi Arabia' and not form.cleaned_data["saudi_mother"]:
            user = User.objects.create_user(form.cleaned_data['username'],
                                            form.cleaned_data['email'],
                                            form.cleaned_data['password1'],
                                            first_name_ar=form.cleaned_data.get('first_name_ar'),
                                            second_name_ar=form.cleaned_data.get('second_name_ar'),
                                            third_name_ar=form.cleaned_data.get('third_name_ar'),
                                            family_name_ar=form.cleaned_data.get('family_name_ar'),
                                            first_name_en=form.cleaned_data.get('first_name_en'),
                                            second_name_en=form.cleaned_data.get('second_name_en'),
                                            third_name_en=form.cleaned_data.get('third_name_en'),
                                            family_name_en=form.cleaned_data.get('family_name_en'),
                                            high_school_graduation_year=form.cleaned_data['high_school_graduation_year'],
                                            status_message=non_saudi_reg_msg,
                                            semester=semester,
                                            nationality=form.cleaned_data['nationality'],
                                            saudi_mother=form.cleaned_data['saudi_mother'],
                                            saudi_mother_gov_id = form.cleaned_data['saudi_mother_gov_id'],
                                            mobile=form.cleaned_data['mobile'],
                                            guardian_mobile=form.cleaned_data['guardian_mobile'],
                                            high_school_gpa_student_entry=
                                            form.cleaned_data['high_school_gpa_student_entry'],
                                            student_notes=form.cleaned_data['student_notes'],
                                            high_school_system=form.cleaned_data['high_school_system'],
                                            )
            SMS.send_sms_registration_success(user.mobile)
            SMS.send_sms_registration_success(user.guardian_mobile)
        else:
            user = User.objects.create_user(form.cleaned_data['username'],
                                            form.cleaned_data['email'],
                                            form.cleaned_data['password1'],
                                            first_name_ar=form.cleaned_data.get('first_name_ar'),
                                            second_name_ar=form.cleaned_data.get('second_name_ar'),
                                            third_name_ar=form.cleaned_data.get('third_name_ar'),
                                            family_name_ar=form.cleaned_data.get('family_name_ar'),
                                            first_name_en=form.cleaned_data.get('first_name_en'),
                                            second_name_en=form.cleaned_data.get('second_name_en'),
                                            third_name_en=form.cleaned_data.get('third_name_en'),
                                            family_name_en=form.cleaned_data.get('family_name_en'),
                                            high_school_graduation_year=form.cleaned_data['high_school_graduation_year'],
                                            status_message=reg_msg,
                                            semester=semester,
                                            nationality=form.cleaned_data['nationality'],
                                            saudi_mother=form.cleaned_data['saudi_mother'],
                                            saudi_mother_gov_id = form.cleaned_data['saudi_mother_gov_id'],
                                            mobile=form.cleaned_data['mobile'],
                                            guardian_mobile=form.cleaned_data['guardian_mobile'],
                                            high_school_gpa_student_entry=
                                            form.cleaned_data['high_school_gpa_student_entry'],
                                            student_notes=form.cleaned_data['student_notes'],
                                            high_school_system=form.cleaned_data['high_school_system'],
                                            )
            SMS.send_sms_registration_success(user.mobile)
            SMS.send_sms_registration_success(user.guardian_mobile)

        Email.send_email_registration_success(user)

        self.request.session['user'] = user.id

        return redirect(self.success_url)


class RegistrationSuccess(TemplateView):
    template_name = 'undergraduate_admission/registration_success.html'

    def get_context_data(self, **kwargs):
        context = super(RegistrationSuccess, self).get_context_data(**kwargs)
        user_id = self.request.session.get('user')
        if user_id is not None:
            context['user'] = get_object_or_404(User, pk=user_id)
        else:
            return redirect('register')

        return context


class EditInfo(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = 'undergraduate_admission/edit_info.html'
    form_class = Phase1UserEditForm
    success_message = _('Info was updated successfully...')
    success_url = reverse_lazy('student_area')

    def get_object(self, queryset=None):
        return self.request.user

    def get_form_kwargs(self):
        kwargs = super(EditInfo, self).get_form_kwargs()
        kwargs['request'] = self.request

        return kwargs
