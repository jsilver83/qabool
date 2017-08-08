from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView
from django.views.generic import FormView
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic import View

from find_roommate.forms import HousingInfoUpdateForm, HousingSearchForm, RoommateRequestForm
from find_roommate.models import HousingUser, RoommateRequest, Room
from undergraduate_admission.forms.phase1_forms import AgreementForm
from undergraduate_admission.models import RegistrationStatusMessage, AdmissionSemester, Agreement, User
from undergraduate_admission.validators import is_eligible_for_housing, is_eligible_for_roommate_search


class HousingBaseView(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.status_message == RegistrationStatusMessage.get_status_admitted() \
               and AdmissionSemester.get_phase4_active_semester(self.request.user)


class HousingLandingPage(HousingBaseView, TemplateView):
    template_name = 'find_roommate/landing_page.html'

    # def test_func(self):
    #     self.login_url = reverse_lazy('housing_agreement')
    #     test_result = super(HousingLandingPage, self).test_func()
    #     agreed = self.request.session.get('agreed', False)
    #     return test_result and agreed

    def get_context_data(self, **kwargs):
        context = super(HousingLandingPage, self).get_context_data(**kwargs)
        context['sent_requests'] = RoommateRequest.objects.filter(requesting_user=self.request.user)
        context['received_requests'] = RoommateRequest.objects.filter(requested_user=self.request.user)
        context['can_make_a_new_request'] = \
            RoommateRequest.objects.filter(Q(requesting_user=self.request.user) |
                                           Q(requested_user=self.request.user),
                                           status__in=[
                                               RoommateRequest.RequestStatuses.PENDING,
                                               RoommateRequest.RequestStatuses.ACCEPTED]).count() == 0
        return context


class HousingAgreement(HousingBaseView, FormView):
    template_name = 'find_roommate/housing_agreement.html'
    form_class = AgreementForm
    agreement_type = 'HOUSING_AGREEMENT'
    next_url = reverse_lazy('housing_landing_page')

    def get_context_data(self, **kwargs):
        context = super(HousingAgreement, self).get_context_data(**kwargs)
        sem = AdmissionSemester.get_phase4_active_semester(self.request.user)
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
    agreement_type = 'HOUSING_ROOMMATE_REQUEST_INSTRUCTIONS'
    success_url = reverse_lazy('housing_landing_page')

    def test_func(self):
        self.login_url = reverse_lazy('housing_landing_page')
        test_result = super(NewRoommateRequest, self).test_func()
        can_make_a_new_request = \
            RoommateRequest.objects.filter(Q(requesting_user=self.request.user) |
                                           Q(requested_user=self.request.user),
                                           status__in=[
                                               RoommateRequest.RequestStatuses.PENDING,
                                               RoommateRequest.RequestStatuses.ACCEPTED]).count() == 0
        return can_make_a_new_request and test_result

    def get_context_data(self, **kwargs):
        context = super(NewRoommateRequest, self).get_context_data(**kwargs)
        sem = AdmissionSemester.get_phase4_active_semester(self.request.user)
        context['agreement'] = get_object_or_404(Agreement, agreement_type=self.agreement_type, semester=sem)
        context['items'] = context['agreement'].items.filter(show=True)
        return context

    def form_valid(self, form):
        gov_id_or_kfupm_id = form.cleaned_data.get('gov_id_or_kfupm_id')
        semester = AdmissionSemester.get_phase4_active_semester(self.request.user)
        roommate = User.objects.filter(Q(kfupm_id=gov_id_or_kfupm_id) |
                                       Q(username=gov_id_or_kfupm_id),
                                       status_message=RegistrationStatusMessage.get_status_admitted(),
                                       eligible_for_housing=True,
                                       semester=semester).exclude(pk=self.request.user.pk).first()
        print(roommate)
        if roommate:
            can_receive_a_new_request = \
                RoommateRequest.objects.filter(Q(requesting_user=roommate) |
                                               Q(requested_user=roommate),
                                               status__in=[
                                                   RoommateRequest.RequestStatuses.PENDING,
                                                   RoommateRequest.RequestStatuses.ACCEPTED]).count() == 0
            print(can_receive_a_new_request)
            if can_receive_a_new_request:
                roommate_request = RoommateRequest()
                roommate_request.requesting_user = self.request.user
                roommate_request.requested_user = roommate
                roommate_request.save()

                messages.success(self.request, _('Request was sent to the student you have chosen...'))
                return redirect(self.success_url)
            else:
                messages.error(self.request, 'The entered KFUPM/Government ID belong to a student who is '
                                             'already a roommate with another student.')
        else:
            messages.error(self.request, 'The entered KFUPM/Government ID doesnt belong to an existing '
                                         'student who is both admitted and eligible for housing')
        return redirect(reverse_lazy('roommate_request'))

    def form_invalid(self, form):
        messages.error(self.request, _('Error.'))
        return super(NewRoommateRequest, self).form_invalid(form)


class AcceptRequest(HousingBaseView, View):
    def get(self, *args, **kwargs):
        roommate_request = RoommateRequest.objects.get(pk=kwargs.get('pk'),
                                                       requested_user=self.request.user,
                                                       status=RoommateRequest.RequestStatuses.PENDING)
        if roommate_request:
            room = Room.get_next_available_room()
            if room:
                roommate_request.assigned_room = room
                roommate_request.status = RoommateRequest.RequestStatuses.ACCEPTED
                roommate_request.save()
                messages.success(self.request, _('Request was accepted and room was assigned to you successfully...'))
            else:
                messages.warning(self.request, _('No rooms are available in the system at the moment. '
                                                 'Kindly try again later!'))
        else:
            messages.error(self.request, _('Invalid request'))
        return redirect('housing_landing_page')


class RejectRequest(HousingBaseView, View):
    def get(self, *args, **kwargs):
        roommate_request = RoommateRequest.objects.get(pk=kwargs.get('pk'),
                                                       requested_user=self.request.user,
                                                       status=RoommateRequest.RequestStatuses.PENDING)
        print(roommate_request)
        if roommate_request:
            roommate_request.status = RoommateRequest.RequestStatuses.REJECTED
            roommate_request.save()
            messages.warning(self.request, _('Request was rejected successfully...'))
        else:
            messages.error(self.request, _('Invalid request'))
        return redirect('housing_landing_page')


@login_required()
@user_passes_test(is_eligible_for_housing)
def housing_info_update(request):
    housing_user, d = HousingUser.objects.get_or_create(user=request.user, defaults={'searchable': False, })
    form = HousingInfoUpdateForm(request.POST or None, instance=housing_user)

    if request.method == 'POST':

        if form.is_valid():
            saved = form.save()
            if saved:
                if saved.searchable:
                    return redirect('housing_search')
                else:
                    return redirect('student_area')
            else:
                messages.error(request, _('Error saving info. Try again later!'))

    return render(request, 'find_roommate/housing_update_form.html', {'form': form, })


@login_required()
@user_passes_test(is_eligible_for_roommate_search)
def housing_search(request):
    students = HousingUser.objects \
        .filter(user__status_message__status_message_code='ADMITTED',
                searchable=True, user__eligible_for_housing=True)
    is_search = False

    if request.GET:
        form = HousingSearchForm(request.GET)
        if form.is_valid():
            try:
                high_school_city = request.GET['high_school_city']
                if high_school_city:
                    students = students.filter(
                        user__high_school_city__contains=high_school_city)

                high_school_name = request.GET['high_school_name']
                if high_school_name:
                    students = students.filter(
                        user__high_school_name__contains=high_school_name)

                light = request.GET['light']
                if light:
                    students = students.filter(light=light)

                room_temperature = request.GET['room_temperature']
                if room_temperature:
                    students = students.filter(room_temperature=room_temperature)

                visits = request.GET['visits']
                if visits:
                    students = students.filter(visits=visits)

                sleeping = request.GET['sleeping']
                if sleeping:
                    students = students.filter(sleeping=sleeping)

                is_search = True

            except MultiValueDictKeyError:
                pass

    else:
        form = HousingSearchForm()

    students_count = students.count()
    paginator = Paginator(students, 10)

    page = request.GET.get('page')
    try:
        objects = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        objects = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        objects = paginator.page(paginator.num_pages)

    return render(request, 'find_roommate/housinguser_list.html', {'page_obj': objects,
                                                                   'form': form,
                                                                   'students_count': students_count,
                                                                   'is_search': is_search, })


@login_required()
@user_passes_test(is_eligible_for_housing)
def housing_letter1(request):
    user = request.user
    assigned_room = Room.get_assigned_room(user)

    return render(request, 'find_roommate/letter_housing.html', {'user': user,
                                                                 'assigned_room': assigned_room, })


@login_required()
@user_passes_test(is_eligible_for_housing)
def housing_letter2(request):
    user = request.user
    assigned_room = Room.get_assigned_room(user)

    return render(request, 'find_roommate/letter_housing_2.html', {'user': user,
                                                                 'assigned_room': assigned_room, })


class PostList(ListView):
    paginate_by = 1

    def get_queryset(self):
        if 'search' in self.request.GET:
            objects = HousingUser.objects.all()
        else:
            objects = HousingUser.objects.all()
        return objects
