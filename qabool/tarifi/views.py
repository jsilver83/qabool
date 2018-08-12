from datetime import timedelta

import requests
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView, FormView

from find_roommate.models import Room
from tarifi.forms import TarifiSearchForm
from .models import *

allowed_statuses_for_tarifi_week = [RegistrationStatusMessage.get_status_admitted_final(),
                                    RegistrationStatusMessage.get_status_admitted_final_non_saudi(),
                                    RegistrationStatusMessage.get_status_admitted_transfer_final()]


class TarifiMixin(UserPassesTestMixin, LoginRequiredMixin):
    login_url = reverse_lazy('admin:index')

    def test_func(self):
        return ((self.request.user.groups.filter(name='Tarifi Staff').exists()
                 or self.request.user.groups.filter(name='Tarifi Admin').exists())
                and self.request.user.is_staff) \
               or self.request.user.is_superuser


class TarifiSimulation(TarifiMixin, TemplateView):
    template_name = 'find_roommate/landing_page.html'

    def get(self, *args, **kwargs):
        users = User.objects.filter(status_message=RegistrationStatusMessage.get_status_admitted_final())[:200]
        counter = 0
        for user in users:
            print(counter)
            tarifi_user, d = TarifiUser.objects.get_or_create(user=user)
            TarifiUser.assign_tarifi_activities(tarifi_user, self.request.user)
            counter += 1
            print(d)

        return redirect('student_area')


class TarifiLandingPage(TarifiMixin, FormView):
    template_name = 'tarifi/landing_page.html'
    form_class = TarifiSearchForm

    def get_context_data(self, **kwargs):
        context = super(TarifiLandingPage, self).get_context_data(**kwargs)
        try:
            now = timezone.now()

            user = User.objects.get(kfupm_id=self.request.GET.get('kfupm_id', -1),
                                    status_message__in=allowed_statuses_for_tarifi_week)
            semester = AdmissionSemester.get_active_semester()
            if semester and user:
                context['student'] = user
                context['show_result'] = True

            context['can_print'] = (user.tarifi_week_attendance_date.slot_start_date <= now <=
                                    user.tarifi_week_attendance_date.slot_end_date) \
                                   or self.request.user.is_superuser \
                                   or self.request.user.groups.filter(name='Tarifi Super Admin').exists()
        except ObjectDoesNotExist:  # the student is not admitted
            if self.request.GET.get('kfupm_id', None):
                context['show_result'] = True
            else:
                context['show_result'] = False
        except AttributeError:  # the student doesnt have a tarifi week attendance date
            context['can_print'] = False
        finally:
            return context

    def get_form(self, form_class=None):
        return self.form_class(self.request.GET or None)


class StudentPrintPage(TarifiMixin, TemplateView):
    template_name = 'tarifi/student_print_page.html'

    def get_context_data(self, **kwargs):
        context = super(StudentPrintPage, self).get_context_data(**kwargs)
        try:
            student = \
                User.objects.get(pk=self.kwargs['pk'],
                                 status_message__in=allowed_statuses_for_tarifi_week)
            context['student'] = student

            tarifi_user, d = TarifiUser.objects.get_or_create(user=student)

            if tarifi_user.preparation_course_slot is None \
                    or tarifi_user.english_placement_test_slot is None \
                    or tarifi_user.english_speaking_test_slot is None:
                TarifiUser.assign_tarifi_activities(tarifi_user, self.request.user)

            context['tarifi_user'] = tarifi_user
            context['reception_box'] = BoxesForIDRanges.objects.filter(from_kfupm_id__lte=student.kfupm_id,
                                                                       to_kfupm_id__gte=student.kfupm_id).first()
            context['issues'] = StudentIssue.objects.filter(kfupm_id=student.kfupm_id,
                                                            show=True)
            context['reception_counter'] = str(student.kfupm_id)[5]
            context['room'] = Room.get_assigned_room(student)
        except ObjectDoesNotExist:
            pass
        finally:
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
                    student = TarifiUser.objects.get(user__kfupm_id=kfupm_id,
                                                     user__semester=semester,
                                                     user__status_message__in=allowed_statuses_for_tarifi_week,
                                                     preparation_course_slot=context['slot'], )

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
                    student = TarifiUser.objects.get(user__kfupm_id=kfupm_id,
                                                     user__semester=semester,
                                                     user__status_message__in=allowed_statuses_for_tarifi_week, )
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
