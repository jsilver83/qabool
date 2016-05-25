from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, get_object_or_404, render
from django.views.decorators.cache import cache_page
from django.views.generic import CreateView
from django.utils.translation import ugettext_lazy as _

from undergraduate_admission.forms.phase1_forms import AgreementForm, RegistrationForm
from undergraduate_admission.models import User, RegistrationStatusMessage, AdmissionSemester, Agreement
from undergraduate_admission.utils import SMS, Email


@cache_page(60 * 15)
def initial_agreement(request):
    form = AgreementForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            request.session['agreed'] = True
            return redirect('register')
        else:
            messages.error(request, _('Error resetting password. Make sure you enter the correct info.'))

    sem = AdmissionSemester.get_phase1_active_semester()
    agreement = get_object_or_404(Agreement, agreement_type='INITIAL', semester=sem)
    agreement_items = agreement.items.all()
    return render(request, 'undergraduate_admission/agreement.html', {'agreement': agreement,
                                                                      'items': agreement_items,
                                                                      'form': form,})


class RegisterView(CreateView):
    model = User
    context_object_name = "user"
    template_name = 'undergraduate_admission/register.html'
    # success_url = reverse_lazy("login")
    form_class = RegistrationForm

    def dispatch(self, request, *args, **kwargs):
        agreed = request.session.get('agreed')
        if agreed is None:
            return redirect('initial_agreement')
        else:
            return super(RegisterView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        reg_msg = RegistrationStatusMessage.objects.get(pk=1) # for status 1 'application submitted'
        semester = AdmissionSemester.get_phase1_active_semester()
        user = User.objects.create_user(form.cleaned_data['username'],
                                        form.cleaned_data['email'],
                                        form.cleaned_data['password1'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'],
                                        high_school_graduation_year=form.cleaned_data['high_school_graduation_year'],
                                        status_message=reg_msg,
                                        semester=semester,
                                        nationality=form.cleaned_data['nationality'],
                                        saudi_mother=form.cleaned_data['saudi_mother'],
                                        mobile=form.cleaned_data['mobile'],
                                        guardian_mobile=form.cleaned_data['guardian_mobile'],
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