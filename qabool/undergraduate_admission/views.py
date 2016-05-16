from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import cache_page

from django.views.generic.edit import CreateView
from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse_lazy, reverse
from django.core.mail import send_mail
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

import requests

from qabool import settings
from .models import User, RegistrationStatusMessage, AdmissionSemester, Agreement
from .forms import RegistrationForm, MyAuthenticationForm, ForgotPasswordForm, AgreementForm
from .utils import SMS, Email


def index(request, template_name='undergraduate_admission/login.html'):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)

                if user.is_superuser:
                    return redirect('/admin')
                else:
                    return redirect(reverse('student_area'))

        else:
            form = MyAuthenticationForm(request.POST)
    else:
        form = MyAuthenticationForm()

    return render(request, template_name, {'form': form})


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
                                        guardian_mobile=form.cleaned_data['guardian_mobile'],)

        SMS.send_sms_registration_success(user.mobile)
        Email.send_email_registration_success(user.email)

        self.request.session['user'] = user.id
        success_url = reverse('registration_success')
        return redirect(success_url)


def registration_success(request):
    userId = request.session.get('user')#request.session['user']
    if userId is not None:
        user = get_object_or_404(User, pk=userId)
        return render(request, 'undergraduate_admission/registration_success.html', context={'user': user})
    else:
        # return redirect(reverse(RegisterView.as_view()))
        return redirect('register')


def forgot_password(request):
    form = ForgotPasswordForm(request.POST or None)

    if request.method == 'POST':
        # form = ForgotPasswordForm(request.POST or None)
        if form.is_valid():
            saved = form.save()
            if saved:
                messages.success(request, _('Password was reset successfully...'))
                return redirect(reverse('index'))
            else:
                messages.error(request, _('Error resetting password. Make sure you enter the correct info.'))

    return render(request, 'undergraduate_admission/forgot_password.html', {'form': form})

@login_required
def student_area(request):
    # user = User.objects.create_user('john7', 'lennon@thebeatles.com', 'johnpassword')
    return render(request, 'undergraduate_admission/student_area.html', context={'user': request.user})


