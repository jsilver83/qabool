import requests
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse_lazy
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.views.generic import DetailView, TemplateView, FormView

from find_roommate.models import Room
from tarifi.forms import TarifiSearchForm
from undergraduate_admission.models import User
from .models import *


class TarifiBaseView(UserPassesTestMixin, LoginRequiredMixin):
    login_url = reverse_lazy('admin:index')

    def test_func(self):
        return ((self.request.user.groups.filter(name='Tarifi Admin').exists()
                 or self.request.user.groups.filter(name='Tarifi Super Admin').exists())
                and self.request.user.is_staff) \
               or self.request.user.is_superuser


class TarifiSimulation(TarifiBaseView, TemplateView):
    template_name = 'find_roommate/landing_page.html'

    def get(self, *args, **kwargs):
        users = User.objects.filter(status_message=RegistrationStatusMessage.get_status_admitted())[:200]
        counter = 0
        for user in users:
            print(counter)
            tarifi_user, d = TarifiUser.objects.get_or_create(user=user)
            TarifiUser.assign_tarifi_activities(tarifi_user, self.request.user)
            counter += 1
            print(d)

        return redirect('student_area')


class TarifiLandingPage(TarifiBaseView, FormView):
    template_name = 'tarifi/landing_page.html'
    form_class = TarifiSearchForm

    def get_context_data(self, **kwargs):
        context = super(TarifiLandingPage, self).get_context_data(**kwargs)
        try:
            now = timezone.now()

            user = User.objects.get(kfupm_id=self.request.GET.get('kfupm_id', -1),
                                    status_message=RegistrationStatusMessage.get_status_admitted(), )
            semester = AdmissionSemester.get_phase4_active_semester()
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


class StudentPrintPage(TarifiBaseView, TemplateView):
    template_name = 'tarifi/student_print_page.html'

    def get_context_data(self, **kwargs):
        context = super(StudentPrintPage, self).get_context_data(**kwargs)
        try:
            student = User.objects.get(pk=self.kwargs['pk'],
                                       status_message=RegistrationStatusMessage.get_status_admitted(), )
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


class CourseAttendance(TarifiBaseView, FormView):
    template_name = 'tarifi/course_attendance.html'
    form_class = TarifiSearchForm

    def get_context_data(self, **kwargs):
        context = super(CourseAttendance, self).get_context_data(**kwargs)

        semester = AdmissionSemester.get_phase4_active_semester()
        now = timezone.now()
        context['now'] = now
        upcoming_slots = TarifiActivitySlot.objects.filter(slot_end_date__gte=now,
                                                           attender=self.request.user,
                                                           type=TarifiActivitySlot.TarifiActivitySlotTypes.PREPARATION_COURSE,
                                                           show=True,
                                                           semester=semester)

        slot = None
        for s in upcoming_slots:
            if s.slot_attendance_start_date <= now <= s.slot_attendance_end_date:
                slot = s
                break

        if slot:
            context['slot'] = slot

            kfupm_id = self.request.GET.get('kfupm_id', -1)
            if kfupm_id != -1:
                try:
                    student = TarifiUser.objects.get(user__kfupm_id=kfupm_id,
                                                     user__semester=semester,
                                                     user__status_message=RegistrationStatusMessage.get_status_admitted(),
                                                     preparation_course_slot=context['slot'], )

                    context['student'] = student
                    student.preparation_course_attendance = now
                    student.preparation_course_attended_by = self.request.user
                    student.save()

                    # make the student attended in Hussain Almuslim bookstore system
                    try:
                        request_link = 'http://10.142.5.182:1345/api/bookstore-update/%s' % (kfupm_id)
                        requests.get(request_link, timeout=(3, 1))
                    except:  # usually TimeoutError but made it general so it will never raise an exception
                        pass
                except ObjectDoesNotExist:
                    pass
            else:
                context['no_student'] = True
        else:
            context['upcoming_slots'] = upcoming_slots
        return context
