from datetime import timedelta

import requests
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView, FormView

from undergraduate_admission.models import AdmissionRequest, RegistrationStatus, AdmissionSemester
from find_roommate.models import Room
from shared_app.utils import UserGroups
from .forms import *
from .models import TarifiActivitySlot, TarifiData, StudentIssue

allowed_statuses_for_tarifi_week = [RegistrationStatus.get_status_admitted_final(),
                                    RegistrationStatus.get_status_admitted_non_saudi_final(),
                                    RegistrationStatus.get_status_admitted_transfer_final()]


class TarifiMixin(UserPassesTestMixin, LoginRequiredMixin):
    login_url = reverse_lazy('admin:index')

    def test_func(self):
        return ((self.request.user.groups.filter(name=UserGroups.TARIFI_STAFF).exists()
                 or self.request.user.groups.filter(name=UserGroups.TARIFI_STAFF).exists())
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


class ReceptionAttendance(TarifiMixin, FormView):
    template_name = 'tarifi/reception_attendance.html'
    form_class = TarifiSearchForm
    login_url = reverse_lazy('tarifi:reception_landing')

    def dispatch(self, request, *args, **kwargs):
        if not(super().test_func() and self.request.session.get('reception_desk', 0)):
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['desk_no'] = self.request.session.get('reception_desk', 0)
        # try:
        now = timezone.now()

        admission_request = AdmissionRequest.objects.get(kfupm_id=self.request.GET.get('kfupm_id', -1),
                                                         semester=AdmissionSemester.get_active_semester() or -1,
                                                         status_message__in=allowed_statuses_for_tarifi_week)
        if admission_request:
            context['student'] = admission_request
            TarifiData.objects.filter(admission_request=admission_request)
            # print(tarifi_data)
            # context['tarifi_data'] = admission_request.tarifi_data
            context['show_result'] = True

        print(context)

        context['can_print'] = ((admission_request.tarifi_week_attendance_date.slot_start_date <= now <=
                                admission_request.tarifi_week_attendance_date.slot_end_date)
                                or self.request.user.is_superuser
                                or self.request.user.groups.filter(name='Tarifi Super Admin').exists())
        # except ObjectDoesNotExist:  # the student is not admitted
        #     if self.request.GET.get('kfupm_id', None):
        #         context['show_result'] = True
        #     else:
        #         context['show_result'] = False
        # except AttributeError:  # the student doesnt have a tarifi week attendance date
        #     context['can_print'] = False
        # finally:
        return context

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
    form_class = TarifiSearchForm

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

        kfupm_id = self.request.GET.get('kfupm_id', -1)
        if slot:
            context['slot'] = slot

            if kfupm_id != -1:
                context['student_entered'] = True
                try:
                    student = TarifiData.objects.get(
                        admission_request__kfupm_id=kfupm_id,
                        admission_request__semester=semester,
                        admission_request__status_message__in=allowed_statuses_for_tarifi_week,
                        preparation_course_slot=context['slot'],
                    )

                    context['student'] = student
                    student.preparation_course_attendance = now
                    student.preparation_course_attended_by = self.request.user
                    student.save()

                    # TODO: make the student attended in Hussain Almuslim bookstore system
                    try:
                        request_link = 'http://10.142.5.182:1345/api/bookstore-update/%s' % kfupm_id
                        requests.get(request_link, timeout=(3, 1))
                    except:  # usually TimeoutError but made it general so it will never raise an exception
                        pass
                except ObjectDoesNotExist:
                    pass
        else:
            if kfupm_id != -1:
                context['student_entered'] = True

                try:
                    student = TarifiData.objects.get(
                        admission_request__kfupm_id=kfupm_id,
                        admission_request__semester=semester,
                        admission_request__status_message__in=allowed_statuses_for_tarifi_week,
                    )
                    context['student'] = student
                    context['slot'] = student.preparation_course_slot
                    context['early_or_late'] = \
                        _('Early') if now < student.preparation_course_slot.slot_attendance_start_date else _('Late')

                    attend_anyways = self.request.GET.get('attend_anyways', 0)
                    if self.request.user.is_superuser or self.request.user.groups.filter(name='Tarifi Admin').exists():
                        context['enable_attendance_anyways'] = True
                        if attend_anyways:
                            student.preparation_course_attendance = now
                            student.preparation_course_attended_by = self.request.user
                            student.save()
                except ObjectDoesNotExist:
                    pass

        return context
