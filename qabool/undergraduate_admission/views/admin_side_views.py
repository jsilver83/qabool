import time

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q, F, Case, When, Value, CharField
from django.http import HttpResponse
from django.shortcuts import render, redirect, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic import UpdateView, View
from extra_views import ModelFormSetView
from floppyforms.__future__ import modelformset_factory

from zeep import Client
from zeep.transports import Transport
import json
import os
import csv

from django.conf import settings
from undergraduate_admission.filters import UserListFilter
from undergraduate_admission.forms.admin_side_forms import CutOffForm, VerifyCommitteeForm, ApplyStatusForm, \
    StudentGenderForm
from undergraduate_admission.models import User, AdmissionSemester, GraduationYear, RegistrationStatusMessage
from undergraduate_admission.utils import try_parse_float, merge_dicts

YESSER_MOE_WSDL = settings.YESSER_MOE_WSDL
YESSER_QIYAS_WSDL = settings.YESSER_QIYAS_WSDL
BASE_DIR = settings.BASE_DIR

# setting soap client requests timeout
transport = Transport(timeout=3)


class AdminBaseView(LoginRequiredMixin, UserPassesTestMixin):
    login_url = reverse_lazy('admin:index')

    def test_func(self):
        return self.request.user.is_superuser


class StaffBaseView(LoginRequiredMixin, UserPassesTestMixin):
    login_url = reverse_lazy('admin:index')

    def test_func(self):
        return self.request.user.is_staff


# TODO: include a mechanism for the null admission total (missing data)
class CutOffPointView(AdminBaseView, View):
    def get_students_matching(self, request):
        selected_student_types = request.GET.getlist('student_type', [])
        selected_high_school_graduation_year = request.GET.getlist('selected_high_school_graduation_year', [])
        # selected_high_school_graduation_year = list(map(int, selected_high_school_graduation_year))
        cut_off_total = try_parse_float(request.GET.get('admission_total', 0.0))
        cut_off_total_operand = request.GET.get('admission_total_operand', 'GTE')
        filtered = UserListFilter(request.GET, queryset=User.objects.filter(is_staff=False))

        filtered_with_properties = filtered.qs.select_related('semester', 'nationality')\
            .annotate(
            admission_percent=F('semester__high_school_gpa_weight') * F('high_school_gpa') / 100
                              + F('semester__qudrat_score_weight') * F('qudrat_score') / 100
                              + F('semester__tahsili_score_weight') * F('tahsili_score') / 100,
            student_nationality_type=Case(When(nationality__nationality_en__icontains='Saudi', then=Value('S')),
                                          When(~ Q(nationality__nationality_en__icontains='Saudi')
                                               & Q(nationality__isnull=False)
                                               & Q(saudi_mother=True),
                                               then=Value('M')),
                                          When(~ Q(nationality__nationality_en__icontains='Saudi')
                                               & Q(nationality__isnull=False)
                                               & (Q(saudi_mother=False) | Q(saudi_mother__isnull=True)),
                                               then=Value('N')),
                                          default=Value('N/A'),
                                          output_field=CharField())) \
            .order_by('-admission_percent')

        if cut_off_total:
            if cut_off_total_operand == 'LT':
                filtered_with_properties = filtered_with_properties.filter(admission_percent__lt=cut_off_total)
            else:
                filtered_with_properties = filtered_with_properties.filter(admission_percent__gte=cut_off_total)

        if selected_high_school_graduation_year:
            filtered_with_properties = filtered_with_properties.filter(
                high_school_graduation_year__in=selected_high_school_graduation_year)

        if selected_student_types:
            filtered_with_properties = filtered_with_properties.filter(
                student_nationality_type__in=selected_student_types)
            # filtered_with_properties = [student for student in filtered.qs
            #                             if student.student_type in selected_student_types]

        return filtered_with_properties

    def get(self, request, *args, **kwargs):
        form = CutOffForm(request.GET or None)
        filtered = self.get_students_matching(request)
        form2 = ApplyStatusForm()
        show_detailed_results = request.GET.get('show_detailed_results', '')

        paginator = Paginator(filtered, 10)
        page = request.GET.get('page')
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        return render(request,
                      template_name='undergraduate_admission/admin/cutoff.html',
                      context={'form': form,
                               'students': page_obj,
                               'students_count': len(filtered),
                               'form2': form2,
                               'show_detailed_results': show_detailed_results})

    def post(self, request, *args, **kwargs):
        # Django Bug: cant update a queryset with annotation; workaround from this:
        # https://stackoverflow.com/questions/13559944/how-to-update-a-queryset-that-has-been-annotated
        filtered = User.objects.filter(pk__in=self.get_students_matching(request))
        form2 = ApplyStatusForm(request.POST or None)

        if form2.is_valid():
            try:
                status = RegistrationStatusMessage.objects.get(pk=form2.cleaned_data.get('status_message'))
                records_updated = filtered.update(status_message = status)
                students_count = filtered.count()
                messages.success(request, _('New status has been applied to %(count)d of %(all)d students chosen...')
                                 % ({'count': records_updated,
                                     'all': students_count}))
            except ObjectDoesNotExist:
                messages.error(request, _('Error in updating status...'))

        return redirect('cut_off_point')


class VerifyList(StaffBaseView, ListView):
    template_name = 'undergraduate_admission/admin/verify_list.html'
    model = User
    context_object_name = 'students'
    paginate_by = 25

    def get_queryset(self):
        logged_in_username = self.request.user.username
        status = [RegistrationStatusMessage.get_status_confirmed()]
        students_to_verified = User.objects.filter(is_staff=False,
                                                   status_message__in=status,
                                                   verification_committee_member= logged_in_username)\
            .order_by('-phase2_submit_date')
        return students_to_verified


class VerifyStudent(StaffBaseView, SuccessMessageMixin, UpdateView):
    template_name = 'undergraduate_admission/admin/verify_committee.html'
    form_class = VerifyCommitteeForm
    model = User
    success_message = _('Verification submitted successfully!!!!')

    def get_success_url(self, **kwargs):
        return reverse_lazy('verify_student', kwargs={'pk': self.kwargs['pk']})


class StudentGenderView(AdminBaseView, TemplateView):
    formset = modelformset_factory(User, form=StudentGenderForm, extra=0)
    template_name = 'undergraduate_admission/admin/student_gender.html'

    def get_context_data(self, **kwargs):
        context = super(StudentGenderView, self).get_context_data(**kwargs)
        sem = AdmissionSemester.get_phase1_active_semester()
        students = User.objects.filter(semester=sem,
                                       is_staff=False,
                                       is_superuser=False).order_by('date_joined')

        paginator = Paginator(students, 25)
        page = self.request.GET.get('page')
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        page_query = students.filter(id__in=[object.id for object in page_obj])
        formset = self.formset(queryset=page_query)
        context['page_obj'] = page_obj
        context['paginator'] = paginator
        context['formset'] = formset
        context['is_paginated'] = True

        return context

    # def get(self, request, *args, **kwargs):
    #     return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        formset = self.formset(request.POST)

        if formset.is_valid():
            for form in formset:
                form.save()
            messages.success(request, _('Gender updated successfully'))

            return render_to_response(self.template_name,
                                      self.get_context_data(**kwargs),
                                      context_instance=RequestContext(request))


class YesserDataUpdate(AdminBaseView, TemplateView):
    template_name = 'undergraduate_admission/admin/yesser_update.html'

    def get_context_data(self, **kwargs):
        context = super(YesserDataUpdate, self).get_context_data(**kwargs)
        sem = AdmissionSemester.get_phase1_active_semester()
        students = User.objects.filter(semester=sem,
                                       is_staff=False,
                                       is_superuser=False)
        context['students_count'] = students.count()

        return context

    def get(self, request, *args, **kwargs):
        manual_update = request.GET.get('manual_update', 0)

        if manual_update:
            sem = AdmissionSemester.get_phase1_active_semester()
            students = User.objects.filter(semester=sem,
                                           is_staff=False,
                                           is_superuser=False)
            for student in students:
                get_student_record_serialized(student)

        return super(YesserDataUpdate, self).get(request, *args, **kwargs)


class QiyasDataUpdate(AdminBaseView, TemplateView):
    def get(self, request, *args, **kwargs):
        serialized_obj = {
            'changed': False,
            'gov_id': 'Not found',
            'student_full_name_ar': 'Not found',
            'status_before': 'Not found',
            'status': 'Not found',
            'high_school_gpa_before': 0.0,
            'high_school_gpa': 0.0,
            'qudrat_before': 0,
            'qudrat': 0,
            'tahsili_before': 0,
            'tahsili': 0,
            'log': '',
            'error': True
        }
        # time.sleep(3)
        page = request.GET.get('page', 1)
        sem = AdmissionSemester.get_phase1_active_semester()
        students = User.objects.filter(semester=sem,
                                       is_staff=False,
                                       is_superuser=False)
        paginator = Paginator(students, 25)
        try:
            student = paginator.page(page).object_list[0]

            serialized_obj = get_student_record_serialized(student)
        except PageNotAnInteger:
            pass
        except EmptyPage:
            pass
        return HttpResponse(json.dumps(serialized_obj), content_type='application/json; charset=utf-8')


def get_student_record_serialized(student, change_status=False):
    final_data = {
        'changed': False,
        'gov_id': '',
        'student_full_name_ar': '',
        'status_before': '',
        'status': '',
        'high_school_gpa_before': 0.0,
        'high_school_gpa': 0.0,
        'qudrat_before': 0,
        'qudrat': 0,
        'tahsili_before': 0,
        'tahsili': 0,
        'log': '',
        'error': True,
    }

    try:
        special_cases_log = ''
        changed = False

        qudrat_data = get_qudrat_from_yesser(student.username)
        tahsili_data = get_tahsili_from_yesser(student.username)
        hs_data = get_high_school_from_yesser(student.username)

        # print(data)
        final_data['status_before'] = student.status_message.status.status_en

        final_data['qudrat_before'] = student.qudrat_score
        if not qudrat_data['q_error']:
            changed = True
            student.first_name_ar = qudrat_data['FirstName']
            student.second_name_ar = qudrat_data['SecondName']
            student.third_name_ar = qudrat_data['ThirdName']
            student.family_name_ar = qudrat_data['LastName']
            student.qudrat_score = qudrat_data['qudrat']

        final_data['tahsili_before'] = student.tahsili_score
        if not tahsili_data['t_error']:
            changed = True
            student.tahsili_score = tahsili_data['tahsili']

        final_data['high_school_gpa_before'] = student.high_school_gpa
        if not hs_data['hs_error']:
            changed = True
            student.high_school_gpa = hs_data['high_school_gpa']
            if hs_data['CertificationHijriYear']:
                year = GraduationYear.get_graduation_year(hs_data['CertificationHijriYear'])
                """
                this is the case of student who entered his hs year wrong
                """
                if year and student.high_school_graduation_year != year:
                    student.high_school_graduation_year = year
                    special_cases_log += '{%s} entered his hs year wrong and got updated<br>' % (student.username)
                    """
                    this is the case of a student who was marked as old hs but actually has recent hs in MOE
                    """
                    if hs_data['CertificationHijriYear'] in ['2015-2016', '2016-2017'] \
                            and student.status_message == RegistrationStatusMessage.get_status_old_high_school():
                        if change_status:
                            student.status_message = RegistrationStatusMessage.get_status_applied()
                        special_cases_log += \
                            '{%s} was marked as old hs but actually has recent hs in MOE<br>' % (student.username)
                """
                this is the case of a student who has old hs status but he has recent hs in his application
                """
                if year and student.high_school_graduation_year == year and \
                                student.status_message == RegistrationStatusMessage.get_status_old_high_school():
                    if change_status:
                        student.status_message = RegistrationStatusMessage.get_status_applied()
                    special_cases_log += \
                        "{%s} has old hs status but he has recent hs in his application<br>" % (student.username)
                """
                this is the case of a student who has old hs
                """
                if not year:
                    try:
                        student.high_school_graduation_year = \
                            GraduationYear.objects.get(description__contains='Other')
                    except ObjectDoesNotExist:
                        other_year = GraduationYear(graduation_year_ar='Other', graduation_year_en='Other',
                                                    description='Other', show=True, display_order=100000)
                        other_year.save()
                        student.high_school_graduation_year = other_year
                    """
                    this is the case of a student who has old hs in MOE but has a status of applied
                    """
                    if student.status_message == RegistrationStatusMessage.get_status_applied():
                        if change_status:
                            student.status_message = RegistrationStatusMessage.get_status_old_high_school()
                        special_cases_log += \
                            '{%s} has old hs in MOE but has a status of applied<br>' % (student.username)
            if hs_data['Gender'] and student.gender != hs_data['Gender']:
                student.gender = hs_data['Gender']
                special_cases_log += '{%s} has his gender changed to {%s}<br>' % (student.username, hs_data['Gender'])
            student.high_school_name = hs_data['SchoolNameAr']
            student.high_school_province = hs_data['AdministrativeAreaNameAr']

        if changed:
            student.save()

        final_data['changed'] = changed
        final_data['gov_id'] = student.username
        final_data['student_full_name_ar'] = student.student_full_name_ar
        final_data['status'] = student.status_message.status.status_en
        final_data['high_school_gpa'] = student.high_school_gpa
        final_data['qudrat'] = student.qudrat_score
        final_data['tahsili'] = student.tahsili_score
        final_data['log'] = special_cases_log
        final_data['error'] = False
    except:
        pass

    return final_data


def get_qudrat_from_yesser(gov_id):
    data = {}
    try:
        client = Client(YESSER_QIYAS_WSDL, transport=transport)
        resultQudrat = client.service.GetExamResult(gov_id, '01', '01')

        if not resultQudrat.ServiceError:
            data['q_error'] = 0
            data['qudrat'] = resultQudrat.GetExamResultResponseDetailObject.ExamResult.ExamResult
            data['FirstName'] = resultQudrat.GetExamResultResponseDetailObject.ApplicantName.PersonNameBody.FirstName
            data['SecondName'] = resultQudrat.GetExamResultResponseDetailObject.ApplicantName.PersonNameBody.SecondName
            data['ThirdName'] = resultQudrat.GetExamResultResponseDetailObject.ApplicantName.PersonNameBody.ThirdName
            data['LastName'] = resultQudrat.GetExamResultResponseDetailObject.ApplicantName.PersonNameBody.LastName
        else:  # no qudrat result from Qiyas
            data['q_error'] = resultQudrat.ServiceError.Code
            data['qudrat'] = 0
            data['FirstName'] = ''
            data['SecondName'] = ''
            data['ThirdName'] = ''
            data['LastName'] = ''
    except:
        data['q_error'] = 'general error'  # Client request message schema validation failure'
        data['qudrat'] = 0
        data['FirstName'] = ''
        data['SecondName'] = ''
        data['ThirdName'] = ''
        data['LastName'] = ''
    return data


def get_tahsili_from_yesser(gov_id):
    data = {}
    try:
        client = Client(YESSER_QIYAS_WSDL, transport=transport)
        resultTahsili = client.service.GetExamResult(gov_id, '02', '01')
        # print(resultTahsili)

        if not resultTahsili.ServiceError:
            data['t_error'] = 0
            data['tahsili'] = resultTahsili.GetExamResultResponseDetailObject.ExamResult.ExamResult
        else:  # no tahsili result from Qiyas
            data['t_error'] = resultTahsili.ServiceError.Code
            data['tahsili'] = 0
    except:
        data['t_error'] = 'general error'
        data['tahsili'] = 0
    return data


def get_high_school_from_yesser(gov_id):
    data = {}
    try:
        client = Client(YESSER_MOE_WSDL, transport=transport)
        result = client.service.GetHighSchoolCertificate(gov_id)

        if not result.ServiceError:
            data['hs_error'] = 0
            data['high_school_gpa'] = result.getHighSchoolCertificateResponseDetailObject. \
                CertificationDetails.GPA
            data['CertificationHijriYear'] = result.getHighSchoolCertificateResponseDetailObject. \
                CertificationDetails.CertificationHijriYear
            data['Gender'] = result.getHighSchoolCertificateResponseDetailObject.StudentBasicInfo.Gender
            data['SchoolNameAr'] = result.getHighSchoolCertificateResponseDetailObject. \
                SchoolInfo.SchoolNameAr
            data['AdministrativeAreaNameAr'] = result.getHighSchoolCertificateResponseDetailObject. \
                SchoolInfo.AdministrativeAreaNameAr
        else:
            data['hs_error'] = result.ServiceError.Code
            data['high_school_gpa'] = 0
            data['CertificationHijriYear'] = ''
            data['Gender'] = ''
            data['SchoolNameAr'] = ''
            data['AdministrativeAreaNameAr'] = ''
    except:
        data['hs_error'] = 'general error'
        data['high_school_gpa'] = 0
        data['CertificationHijriYear'] = ''
        data['Gender'] = ''
        data['SchoolNameAr'] = ''
        data['AdministrativeAreaNameAr'] = ''
    return data
