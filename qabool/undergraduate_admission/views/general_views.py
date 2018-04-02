import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.http import is_safe_url
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView

from qabool import settings
from qabool.local_settings import API_SECURITY_TOKEN
from undergraduate_admission.forms.general_forms import MyAuthenticationForm, ForgotPasswordForm, BaseContactForm
from undergraduate_admission.models import AdmissionSemester, RegistrationStatusMessage, User


def index(request, template_name='undergraduate_admission/login.html'):
    form = MyAuthenticationForm(request.POST or None)

    redirect_to = request.POST.get('next',
                                   request.GET.get('next', reverse_lazy('student_area')))

    if request.method == 'GET' and request.user.is_authenticated(): return redirect(reverse('student_area'))

    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    # if not is_safe_url(url=redirect_to, host=request.get_host()):
                    #     redirect_to = reverse('student_area')
                    return redirect(redirect_to)

    phase1_active = False
    if AdmissionSemester.check_if_phase1_is_active():
        phase1_active = True

    return render(request, template_name, {
        'form': form,
        'phase1_active': phase1_active,
        'next': redirect_to,
    })


def forgot_password(request):
    form = ForgotPasswordForm(request.POST or None)

    if request.method == 'POST':
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
    phase = request.user.get_student_phase()

    status_message = request.user.status_message

    show_result = phase in ['PARTIALLY-ADMITTED', 'REJECTED']

    can_confirm = phase == 'PARTIALLY-ADMITTED' \
                  and status_message != RegistrationStatusMessage.get_status_confirmed() \
                  and status_message != RegistrationStatusMessage.get_status_confirmed_non_saudi() \
                  and AdmissionSemester.get_phase2_active_semester(request.user)

    can_finish_phase3 = phase == 'ADMITTED' \
                        and not request.user.tarifi_week_attendance_date \
                        and AdmissionSemester.get_phase3_active_semester(request.user)

    can_re_upload_docs = phase == 'PARTIALLY-ADMITTED' and request.user.verification_documents_incomplete

    can_re_upload_picture = phase == 'PARTIALLY-ADMITTED' and request.user.verification_picture_acceptable

    can_upload_withdrawal_proof = status_message == RegistrationStatusMessage.get_status_duplicate()

    return render(request,
                  'undergraduate_admission/student_area.html', context={'user': request.user,
                                                                        'show_result': show_result,
                                                                        'can_confirm': can_confirm,
                                                                        'can_re_upload_docs': can_re_upload_docs,
                                                                        'can_re_upload_picture': can_re_upload_picture,
                                                                        'can_upload_withdrawal_proof':
                                                                            can_upload_withdrawal_proof,
                                                                        'can_finish_phase3': can_finish_phase3,
                                                                        })


class EditContactInfo(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = 'undergraduate_admission/edit_contact_info.html'
    form_class = BaseContactForm
    success_message = _('Contact Info was updated successfully...')
    success_url = reverse_lazy('student_area')

    def get_object(self, queryset=None):
        return self.request.user

    def get_form_kwargs(self):
        kwargs = super(EditContactInfo, self).get_form_kwargs()
        kwargs['request'] = self.request

        return kwargs


def csrf_failure(request, reason=""):
    return render(request, 'undergraduate_admission/csrf_failure.html')


def check_student_status(kfupm_id, security_token):
    try:
        if security_token == API_SECURITY_TOKEN:
            student_status = User.objects.get(kfupm_id=kfupm_id).get_student_phase()

            if student_status == 'ADMITTED':
                return 'ADMITTED'
            else:
                return 'NOT'
        else:
            return 'WRONG TOKEN'

    except ObjectDoesNotExist:
        return 'STUDENT DOESNT EXIST'
    except:
        return 'GENERAL ERROR'


# @csrf_exempt
def check_if_student_is_admitted(request):
    if request.method == 'GET':
        security_token = request.GET['security_token']
        kfupm_id = request.GET['kfupm_id']

        return HttpResponse(check_student_status(kfupm_id, security_token))
    else:
        return HttpResponse('VERB NOT ALLOWED')


# @csrf_exempt
def mark_student_as_attended(request):
    if request.method == 'GET':
        security_token = request.GET['security_token']
        kfupm_id = request.GET['kfupm_id']

        result = check_student_status(kfupm_id, security_token)

        if result == 'ADMITTED':
            user = User.objects.get(kfupm_id=kfupm_id)
            if user:
                user.tarifi_week_attendance_date = timezone.now()
                user.save()
                return HttpResponse('DONE')
        else:
            return HttpResponse(result)
    else:
        return HttpResponse('VERB NOT ALLOWED')
