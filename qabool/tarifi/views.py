from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, redirect
from django.views.generic import DetailView, TemplateView, FormView

from tarifi.forms import TarifiSearchForm
from undergraduate_admission.models import User
from .models import *


class TarifiBaseView(UserPassesTestMixin, LoginRequiredMixin):
    login_url = reverse_lazy('admin:index')

    def test_func(self):
        return ('Tarifi Admin' in self.request.user.groups.all()
                and self.request.user.is_staff) \
               or self.request.user.is_superuser


class TarifiSimulation(TarifiBaseView, TemplateView):
    template_name = 'find_roommate/landing_page.html'

    def get(self, *args, **kwargs):
        users = User.objects.all()[:60]
        counter = 0
        for user in users:
            print(counter)
            tarifi_user, d = TarifiUser.objects.get_or_create(user=user)
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
                                   or 'Tarifi Super Admin' in self.request.user.groups.all()
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
        print(self.request.user)
        # try:
        student = User.objects.get(pk=self.kwargs['pk'],
                                   status_message=RegistrationStatusMessage.get_status_admitted(), )
        context['student'] = student
        tarifi_user, d = TarifiUser.objects.get_or_create(user=student, received_by=self.request.user)
        context['tarifi_user'] = tarifi_user
        context['reception_box'] = BoxesForIDRanges.objects.filter(from_kfupm_id__lte=student.kfupm_id,
                                                                   to_kfupm_id__gte=student.kfupm_id).first()
        context['issues'] = StudentIssue.objects.filter(kfupm_id=student.kfupm_id,
                                                        show=True)
        context['reception_counter'] = str(student.kfupm_id)[5]
        # except ObjectDoesNotExist:
        #     pass
        # finally:
        return context


class CourseAttendance(TarifiBaseView, FormView):
    template_name = 'tarifi/course_attendance.html'
    form_class = TarifiSearchForm

    def get_context_data(self, **kwargs):
        context = super(CourseAttendance, self).get_context_data(**kwargs)

        semester = AdmissionSemester.get_phase4_active_semester()
        now = timezone.now()
        context['now'] = now
        acceptable_slot_start_date = now - timezone.timedelta(minutes=60)
        acceptable_slot_end_date = now + timezone.timedelta(minutes=60)
        slots = TarifiActivitySlot.objects.filter(slot_start_date__gte=acceptable_slot_start_date,
                                                  slot_end_date__lte=acceptable_slot_end_date,
                                                  attender=self.request.user,
                                                  type=TarifiActivitySlot.TarifiActivitySlotTypes.PREPARATION_COURSE,
                                                  show=True,
                                                  semester=semester)
        if slots.count() == 1:
            context['slot'] = slots.first()

            kfupm_id = self.request.GET.get('kfupm_id', -1)
            if kfupm_id != -1:
                try:
                    student = TarifiUser.objects.get(user__kfupm_id=kfupm_id,
                                                     user__semester=semester,
                                                     user__status_message=RegistrationStatusMessage.get_status_admitted(),
                                                     preparation_course_slot=context['slot'],)

                    context['student'] = student
                    student.preparation_course_attendance_date = now
                    student.preparation_course_attended_by = self.request.user
                    student.save()
                except ObjectDoesNotExist:
                    pass
            else:
                context['no_student'] = True

        return context

