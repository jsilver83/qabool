from datetime import timedelta

import requests
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView, FormView

from find_roommate.models import Room
from shared_app.utils import UserGroups
from undergraduate_admission.models import AdmissionRequest, RegistrationStatus, AdmissionSemester
from .forms import *
from .models import TarifiActivitySlot, TarifiData, StudentIssue

allowed_statuses_for_tarifi_week = [RegistrationStatus.get_status_admitted_final(),
                                    RegistrationStatus.get_status_admitted_non_saudi_final(),
                                    RegistrationStatus.get_status_admitted_transfer_final()]


class TarifiMixin(UserPassesTestMixin, LoginRequiredMixin):
    login_url = reverse_lazy('admin:index')

    def test_func(self):
        return ((self.request.user.groups.filter(name=UserGroups.TARIFI_STAFF).exists()
                 or self.request.user.groups.filter(name=UserGroups.TARIFI_ADMIN).exists())
                and self.request.user.is_staff) \
               or self.request.user.is_superuser


class TarifiSimulation(TarifiMixin, TemplateView):
    template_name = 'find_roommate/landing_page.html'

    def get(self, *args, **kwargs):
        admission_request = AdmissionRequest.objects.filter(
            status_message__in=allowed_statuses_for_tarifi_week,
            semester__active=True,
        )[:200]
        counter = 0
        for admission_request in admission_request:
            print(counter)
            tarifi_data, d = TarifiData.objects.get_or_create(admission_request=admission_request)
            tarifi_data.receive(self.request.user, use_current_timing=True, reschedule=True)
            counter += 1
            print(d)

        return redirect('undergraduate_admission:student_area')


class ReceptionLanding(TarifiMixin, FormView):
    template_name = 'tarifi/reception_landing.html'
    form_class = ReceptionDeskForm
    success_url = reverse_lazy('tarifi:reception')

    def form_valid(self, form):
        self.request.session['reception_desk'] = form.cleaned_data.get('reception_desk', 0)
        messages.success(self.request, _('Desk number specified successfully...'))
        return super().form_valid(form)


# TODO: use post-based form to search and attend
class ReceptionAttendance(TarifiMixin, FormView):
    template_name = 'tarifi/reception_attendance.html'
    form_class = TarifiSearchForm
    login_url = reverse_lazy('tarifi:reception_landing')
    success_url = reverse_lazy('tarifi:reception')

    def dispatch(self, request, *args, **kwargs):
        if not(super().test_func() and self.request.session.get('reception_desk', 0)):
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    @staticmethod
    def get_object(kfupm_id_gov_id):
        return AdmissionRequest.objects.get(
                    Q(kfupm_id=kfupm_id_gov_id) | Q(user__username=kfupm_id_gov_id),
                    semester=AdmissionSemester.get_active_semester() or -1,
                    status_message__in=allowed_statuses_for_tarifi_week
                )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['desk_no'] = self.request.session.get('reception_desk', 0)
        if self.request.GET.get('kfupm_id_gov_id', 0):
            context['show_result'] = True
            try:
                now = timezone.now()

                admission_request = self.get_object(self.request.GET.get('kfupm_id_gov_id', 0))

                if admission_request:
                    context['student'] = admission_request
                    tarifi_data, created = TarifiData.objects.get_or_create(admission_request=admission_request)
                    context['tarifi_data'] = tarifi_data
                    context['show_result'] = True

                    context['wrong_desk'] = context['desk_no'] != (tarifi_data.desk_no or 0)

                    context['can_print'] = ((admission_request.tarifi_week_attendance_date.slot_start_date <= now <=
                                            admission_request.tarifi_week_attendance_date.slot_end_date
                                             and not context['wrong_desk'])
                                            or self.request.user.is_superuser
                                            or self.request.user.groups.filter(name=UserGroups.TARIFI_ADMIN).exists())
            except ObjectDoesNotExist:  # the student is not admitted
                pass
            except AttributeError:  # the student doesnt have a tarifi week attendance date
                context['can_print'] = False

        else:
            context['show_result'] = False

        return context

    def form_valid(self, form):
        admission_request = self.get_object(self.request.GET.get('kfupm_id_gov_id', 0))
        if 'attend' in self.request.POST:
            admission_request.tarifi_data.received_by = self.request.user
            admission_request.tarifi_data.save()
            messages.success(self.request, _('{} was attended successfully'.format(admission_request)))
        elif 'cancel' in self.request.POST:
            messages.warning(self.request, _('You chose to cancel attending {}'.format(admission_request)))
        return super().form_valid(form)

    def get_form(self, form_class=None):
        return self.form_class(self.request.GET or None)


class StudentPrintPage(TarifiMixin, TemplateView):
    template_name = 'tarifi/student_print_page.html'

    def get_context_data(self, **kwargs):
        context = super(StudentPrintPage, self).get_context_data(**kwargs)

        student = get_object_or_404(
            AdmissionRequest,
            pk=self.kwargs['pk'],
            status_message__in=allowed_statuses_for_tarifi_week
        )
        context['student'] = student

        context['tarifi_data'] = getattr(student, 'tarifi_data')

        context['issues'] = StudentIssue.objects.filter(kfupm_id=student.kfupm_id,
                                                        show=True)
        context['room'] = Room.get_assigned_room(student)

        return context


class CourseAttendance(TarifiMixin, FormView):
    template_name = 'tarifi/course_attendance.html'
    form_class = CourseAttendanceSearchForm

    def get_context_data(self, **kwargs):
        context = super(CourseAttendance, self).get_context_data(**kwargs)

        semester = AdmissionSemester.get_active_semester()
        now = timezone.now()
        context['now'] = now
        now_minus_15_minutes = now + timedelta(minutes=-15)
        now_plus_15_minutes = now + timedelta(minutes=15)
        slot = TarifiActivitySlot.objects.filter(slot_start_date__gte=now_minus_15_minutes,
                                                 slot_start_date__lte=now_plus_15_minutes,
                                                 attender=self.request.user,
                                                 type=TarifiActivitySlot.TarifiActivitySlotTypes.PREPARATION_COURSE,
                                                 show=True,
                                                 semester=semester).first()
        context['slot'] = slot

        kfupm_id = self.request.GET.get('kfupm_id', 0)

        if kfupm_id:
            context['student_entered'] = True

            try:
                student = TarifiData.objects.get(
                    admission_request__kfupm_id=kfupm_id,
                    admission_request__semester=semester,
                    admission_request__status_message__in=allowed_statuses_for_tarifi_week,
                )

                context['student'] = student

                if (student.preparation_course_slot == context['slot'] or self.request.user.is_superuser
                        or self.request.user.groups.filter(name=UserGroups.TARIFI_ADMIN).exists()):
                    if student.preparation_course_attendance is None or student.preparation_course_attended_by is None:
                        student.preparation_course_attendance = now
                        student.preparation_course_attended_by = self.request.user
                        student.save()
                    context['attended'] = True
                else:
                    context['attended'] = False

                context['early_or_late'] = \
                        _('Early') if now < student.preparation_course_slot.slot_start_date else _('Late')

                # TODO: make the student attended in Hussain Almuslim bookstore system
                try:
                    request_link = 'http://10.142.5.182:1345/api/bookstore-update/%s' % kfupm_id
                    requests.get(request_link, timeout=(3, 1))
                except:  # usually TimeoutError but made it general so it will never raise an exception
                    pass
            except ObjectDoesNotExist:
                pass

        return context
