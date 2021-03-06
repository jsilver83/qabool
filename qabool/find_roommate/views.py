from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView
from django.views.generic import TemplateView
from django.views.generic import UpdateView
from django.views.generic import View
from django_filters.views import FilterView

from shared_app.base_forms import BaseCrispyForm
from .filters import HousingUserFilter
from .forms import HousingInfoUpdateForm, HousingSearchForm, RoommateRequestForm
from .models import HousingUser, RoommateRequest, Room
from shared_app.base_views import StudentMixin
from undergraduate_admission.forms.phase1_forms import AgreementForm
from undergraduate_admission.models import RegistrationStatus, AdmissionSemester, Agreement, AdmissionRequest
from undergraduate_admission.utils import SMS


allowed_statuses_for_housing = [RegistrationStatus.get_status_admitted_final(),
                                RegistrationStatus.get_status_admitted_non_saudi_final(),
                                RegistrationStatus.get_status_admitted_transfer_final()]


class HousingBaseView(StudentMixin):
    def test_func(self):
        super_test_result = super().test_func()
        return (super_test_result and self.admission_request.status_message in allowed_statuses_for_housing
                and self.admission_request.eligible_for_housing and AdmissionSemester.get_phase4_active_semester())


class HousingLandingPage(HousingBaseView, TemplateView):
    template_name = 'find_roommate/landing_page.html'

    # def test_func(self):
    #     self.login_url = reverse_lazy('housing_agreement')
    #     test_result = super(HousingLandingPage, self).test_func()
    #     agreed = self.request.session.get('agreed', False)
    #     return test_result and agreed

    def get_context_data(self, **kwargs):
        context = super(HousingLandingPage, self).get_context_data(**kwargs)
        context['admission_request'] = self.admission_request
        context['sent_requests'] = RoommateRequest.objects.filter(requesting_user=self.admission_request)
        context['received_requests'] = RoommateRequest.objects.filter(requested_user=self.admission_request)
        context['can_make_a_new_request'] = \
            RoommateRequest.objects.filter(Q(requesting_user=self.admission_request) |
                                           Q(requested_user=self.admission_request),
                                           status__in=[
                                               RoommateRequest.RequestStatuses.PENDING,
                                               RoommateRequest.RequestStatuses.ACCEPTED]).count() == 0
        return context


class HousingAgreement(HousingBaseView, FormView):
    template_name = 'find_roommate/housing_agreement.html'
    form_class = AgreementForm
    agreement_type = 'HOUSING_AGREEMENT'
    next_url = reverse_lazy('find_roommate:housing_landing_page')

    def get_context_data(self, **kwargs):
        context = super(HousingAgreement, self).get_context_data(**kwargs)
        sem = AdmissionSemester.get_phase4_active_semester()
        context['agreement'] = get_object_or_404(Agreement, agreement_type=self.agreement_type, semester=sem)
        context['items'] = context['agreement'].items.filter(show=True)
        return context

    def form_valid(self, form):
        self.request.session['agreed'] = True
        return redirect(self.next_url)

    def form_invalid(self, form):
        messages.error(self.request, _('Error.'))
        return super(HousingAgreement, self).form_invalid(form)


class NewRoommateRequest(HousingBaseView, FormView):
    template_name = 'find_roommate/request_roommate.html'
    form_class = RoommateRequestForm
    agreement_type = Agreement.AgreementTypes.HOUSING_ROOMMATE_REQUEST_INSTRUCTIONS
    success_url = reverse_lazy('find_roommate:housing_landing_page')

    def test_func(self):
        self.login_url = reverse_lazy('find_roommate:housing_landing_page')
        test_result = super(NewRoommateRequest, self).test_func()
        can_make_a_new_request = \
            RoommateRequest.objects.filter(Q(requesting_user=self.admission_request) |
                                           Q(requested_user=self.admission_request),
                                           status__in=[
                                               RoommateRequest.RequestStatuses.PENDING,
                                               RoommateRequest.RequestStatuses.ACCEPTED]).count() == 0
        return can_make_a_new_request and test_result

    def get_context_data(self, **kwargs):
        context = super(NewRoommateRequest, self).get_context_data(**kwargs)
        sem = AdmissionSemester.get_phase4_active_semester()
        context['agreement'] = get_object_or_404(Agreement, agreement_type=self.agreement_type, semester=sem)
        return context

    def form_valid(self, form):
        gov_id_or_kfupm_id = form.cleaned_data.get('gov_id_or_kfupm_id')
        semester = AdmissionSemester.get_phase4_active_semester()
        roommate = AdmissionRequest.objects.filter(Q(kfupm_id=gov_id_or_kfupm_id) |
                                                   Q(user__username=gov_id_or_kfupm_id),
                                                   status_message__in=allowed_statuses_for_housing,
                                                   eligible_for_housing=True,
                                                   semester=semester).exclude(pk=self.admission_request.pk).first()

        if roommate:
            can_receive_a_new_request = \
                RoommateRequest.objects.filter(Q(requesting_user=roommate) |
                                               Q(requested_user=roommate),
                                               status__in=[
                                                   RoommateRequest.RequestStatuses.PENDING,
                                                   RoommateRequest.RequestStatuses.ACCEPTED]).count() == 0

            if can_receive_a_new_request:
                roommate_request = RoommateRequest()
                roommate_request.requesting_user = self.admission_request
                roommate_request.requested_user = roommate
                roommate_request.save()

                SMS.send_sms_housing_roommate_request_sent(roommate_request.requested_user.mobile)
                messages.success(self.request, _('Request was sent to the student you have chosen...'))
                return redirect(self.success_url)
            else:
                student_has_pending_requests = \
                    RoommateRequest.objects.filter(Q(requesting_user=roommate) |
                                                   Q(requested_user=roommate),
                                                   status=RoommateRequest.RequestStatuses.PENDING).count() > 0

                if student_has_pending_requests:
                    messages.error(self.request, _('The entered KFUPM ID belong to a student who has '
                                                   'a pending roommate request.'))
                else:
                    messages.error(self.request, _('The entered KFUPM ID belong to a student who already has '
                                                   'a roommate.'))
        else:
            messages.error(self.request, _('The entered KFUPM ID doesnt belong to an existing '
                                           'student who is both admitted and eligible for housing'))
        return redirect('find_roommate:roommate_request')

    def form_invalid(self, form):
        messages.error(self.request, _('Error.'))
        return super(NewRoommateRequest, self).form_invalid(form)


def check_remaining_rooms_threshold():
    remaining_rooms = Room.objects.filter(available=True). \
        exclude(pk__in=RoommateRequest.objects.filter(status=RoommateRequest.RequestStatuses.ACCEPTED)
                .values_list('assigned_room', flat=True)).count()

    if remaining_rooms == 10:
        SMS.send_sms_housing_rooms_threshold_10()

    elif remaining_rooms == 50:
        SMS.send_sms_housing_rooms_threshold_50()

    elif remaining_rooms == 100:
        SMS.send_sms_housing_rooms_threshold_100()


class AcceptRequest(HousingBaseView, FormView):
    template_name = 'find_roommate/accept_request.html'
    form_class = AgreementForm
    agreement_type = Agreement.AgreementTypes.HOUSING_AGREEMENT
    next_url = reverse_lazy('find_roommate:housing_landing_page')

    def get_context_data(self, **kwargs):
        context = super(AcceptRequest, self).get_context_data(**kwargs)
        sem = AdmissionSemester.get_phase4_active_semester()
        context['agreement'] = get_object_or_404(Agreement, agreement_type=self.agreement_type, semester=sem)
        context['admission_request'] = self.admission_request
        return context

    def form_valid(self, form):
        roommate_request = RoommateRequest.objects.get(pk=self.kwargs.get('pk'),
                                                       requested_user=self.admission_request,
                                                       status=RoommateRequest.RequestStatuses.PENDING)
        if roommate_request:
            room = Room.get_next_available_room()
            if room:
                roommate_request.assigned_room = room
                roommate_request.status = RoommateRequest.RequestStatuses.ACCEPTED
                roommate_request.save()

                SMS.send_sms_housing_roommate_request_accepted(roommate_request.requesting_user.mobile)
                check_remaining_rooms_threshold()
                messages.success(self.request, _('Request was accepted and room was assigned to you successfully...'))
            else:
                messages.warning(self.request, _('There was an issue in assigning a room to you. '
                                                 'Kindly try again in 24 hours!'))
        else:
            messages.error(self.request, _('Invalid request'))
        return redirect(self.next_url)

    def form_invalid(self, form):
        messages.error(self.request, _('Error.'))
        return super(AcceptRequest, self).form_invalid(form)


class RejectRequest(HousingBaseView, View):
    def get(self, *args, **kwargs):
        roommate_request = RoommateRequest.objects.get(pk=kwargs.get('pk'),
                                                       requested_user=self.admission_request,
                                                       status=RoommateRequest.RequestStatuses.PENDING)

        if roommate_request:
            roommate_request.status = RoommateRequest.RequestStatuses.REJECTED
            roommate_request.save()

            SMS.send_sms_housing_roommate_request_rejected(roommate_request.requesting_user.mobile)
            messages.warning(self.request, _('Request was rejected successfully...'))
        else:
            messages.error(self.request, _('Invalid request'))
        return redirect('find_roommate:housing_landing_page')


class CancelRequest(HousingBaseView, View):
    def get(self, *args, **kwargs):
        roommate_request = RoommateRequest.objects.get(pk=kwargs.get('pk'),
                                                       requesting_user=self.admission_request,
                                                       status=RoommateRequest.RequestStatuses.PENDING)

        if roommate_request:
            roommate_request.status = RoommateRequest.RequestStatuses.CANCELLED
            roommate_request.save()
            messages.warning(self.request, _('Request was cancelled as per your request...'))
        else:
            messages.error(self.request, _('Invalid request'))
        return redirect('find_roommate:housing_landing_page')


class HousingInfoUpdate(HousingBaseView, UpdateView):
    template_name = 'find_roommate/housing_update_form.html'
    form_class = HousingInfoUpdateForm
    agreement_type = Agreement.AgreementTypes.HOUSING_ROOMMATE_SEARCH_INSTRUCTIONS
    success_url = reverse_lazy('find_roommate:housing_search')
    housing_user = None

    def test_func(self):
        self.login_url = reverse_lazy('find_roommate:housing_landing_page')
        test_result = super(HousingInfoUpdate, self).test_func()
        can_search = \
            RoommateRequest.objects.filter(Q(requesting_user=self.admission_request) |
                                           Q(requested_user=self.admission_request),
                                           status__in=[
                                               RoommateRequest.RequestStatuses.PENDING,
                                               RoommateRequest.RequestStatuses.ACCEPTED]).count() == 0
        return can_search and test_result

    def dispatch(self, request, *args, **kwargs):
        self.init_class_variables(request)
        self.housing_user, d = HousingUser.objects.get_or_create(user=self.admission_request,
                                                                 defaults={'searchable': False, })
        return super(HousingInfoUpdate, self).dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.housing_user

    def get_context_data(self, **kwargs):
        context = super(HousingInfoUpdate, self).get_context_data(**kwargs)
        sem = AdmissionSemester.get_phase4_active_semester()
        context['agreement'] = get_object_or_404(Agreement, agreement_type=self.agreement_type, semester=sem)
        return context

    def form_valid(self, form):
        saved = form.save()
        if saved:
            if saved.searchable:
                return redirect('find_roommate:housing_search')
            else:
                return redirect('undergraduate_admission:student_area')
        else:
            messages.error(self.request, _('Error saving info. Try again later!'))
        return redirect('undergraduate_admission:student_area')


class HousingSearch(HousingBaseView, FilterView):
    filterset_class = HousingUserFilter
    template_name = 'find_roommate/housinguser_list.html'
    paginate_by = 10
    strict = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['search_form'] = BaseCrispyForm
        context['admission_request'] = self.admission_request

        return context


class BaseHousingLetter(HousingBaseView, TemplateView):
    def get_context_data(self, **kwargs):
        context = super(BaseHousingLetter, self).get_context_data(**kwargs)
        context['student'] = self.admission_request
        context['assigned_room'] = Room.get_assigned_room(self.admission_request)
        context['date'] = RoommateRequest.objects.filter(Q(requesting_user=self.admission_request) |
                                                         Q(requested_user=self.admission_request),
                                                         status=RoommateRequest.RequestStatuses.ACCEPTED).first().updated_on

        return context


class HousingLetter1(BaseHousingLetter):
    template_name = 'find_roommate/letter_housing.html'


class HousingLetter2(BaseHousingLetter):
    template_name = 'find_roommate/letter_housing_2.html'


class HousingLetter3(BaseHousingLetter):
    template_name = 'find_roommate/letter_housing_3.html'
