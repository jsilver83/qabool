from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, get_object_or_404, render
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_protect
from django.views.generic import CreateView
from django.utils.translation import ugettext_lazy as _
from django.core.cache import cache

from undergraduate_admission.filters import UserListFilter
from undergraduate_admission.forms.phase1_forms import AgreementForm, RegistrationForm, EditInfoForm, Phase1UserEditForm, \
    CutOffForm
from undergraduate_admission.models import User, RegistrationStatusMessage, AdmissionSemester, Agreement, ImportantDateSidebar
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
                                                                      'form': form,})

class RegisterView(CreateView):
    model = User
    context_object_name = "user"
    template_name = 'undergraduate_admission/register.html'
    # success_url = reverse_lazy("login")
    form_class = RegistrationForm

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
        semester = AdmissionSemester.get_phase1_active_semester()
        user = User.objects.create_user(form.cleaned_data['username'],
                                        form.cleaned_data['email'],
                                        form.cleaned_data['password1'],
                                        student_full_name_ar=form.cleaned_data['student_full_name_ar'],
                                        student_full_name_en=form.cleaned_data['student_full_name_en'],
                                        high_school_graduation_year=form.cleaned_data['high_school_graduation_year'],
                                        status_message=reg_msg,
                                        semester=semester,
                                        nationality=form.cleaned_data['nationality'],
                                        saudi_mother=form.cleaned_data['saudi_mother'],
                                        mobile=form.cleaned_data['mobile'],
                                        guardian_mobile=form.cleaned_data['guardian_mobile'],
                                        high_school_gpa=form.cleaned_data['high_school_gpa'],
                                        # qudrat_score=form.cleaned_data['qudrat_score'],
                                        # tahsili_score=form.cleaned_data['tahsili_score'],
                                        student_notes=form.cleaned_data['student_notes'],
                                        high_school_system=form.cleaned_data['high_school_system'],
                                        )

        SMS.send_sms_registration_success(user.mobile)
        Email.send_email_registration_success(user)

        self.request.session['user'] = user.id
        success_url = reverse('registration_success')
        return redirect(success_url)


def registration_success(request):
    user_id = request.session.get('user')
    if user_id is not None:
        user = get_object_or_404(User, pk=user_id)
        return render(request, 'undergraduate_admission/registration_success.html', context={'user': user})
    else:
        return redirect('register')


@login_required()
def edit_info(request):
    form = Phase1UserEditForm(request.POST or None, instance=request.user, request=request)

    if request.method == 'POST':
        if form.is_valid():
            saved = form.save()
            if saved:
                messages.success(request, _('Info was updated successfully...'))
                return redirect('student_area')
            else:
                messages.error(request, _('Error updating info. Try again later!'))

    return render(request, 'undergraduate_admission/edit_info.html', context={'form': form})


def cut_off_point(request):
    form = CutOffForm(request.GET or None)
    selected_student_types = request.GET.getlist('student_type', ['S', 'M', 'N'])
    print(selected_student_types)
    cut_off_total = try_parse_float(request.GET.get('admission_total', 0.0))
    print(cut_off_total)

    filtered = UserListFilter(request.GET, queryset=User.objects.all())
    filtered_with_properties = [student for student in filtered.qs
                                if student.student_type in selected_student_types]
    filtered_with_properties = [student for student in filtered_with_properties
                                if student.admission_total > cut_off_total]

    return render(request,
                  template_name='undergraduate_admission/phase3/cutoff.html',
                  context={'form': form, 'students': filtered_with_properties})