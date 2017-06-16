import time
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse
from django.shortcuts import render, redirect, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from django.views.generic import UpdateView, View
from extra_views import ModelFormSetView
from floppyforms.__future__ import modelformset_factory

from zeep import Client
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


class AdminBaseView(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser


class CutOffPointView(AdminBaseView, View):
    def get_students_matching(self, request):
        selected_student_types = request.GET.getlist('student_type', ['S', 'M', 'N'])
        # print(selected_student_types)
        cut_off_total = try_parse_float(request.GET.get('admission_total', 0.0))
        # print(cut_off_total)

        filtered = UserListFilter(request.GET, queryset=User.objects.all())
        filtered_with_properties = [student for student in filtered.qs
                                    if student.student_type in selected_student_types]
        filtered_with_properties2 = [student for student in filtered_with_properties
                                     if student.admission_total >= cut_off_total]

        return filtered_with_properties2

    def get(self, request, *args, **kwargs):
        form = CutOffForm(request.GET or None)

        filtered = self.get_students_matching(request)

        form2 = ApplyStatusForm()

        return render(request,
                      template_name='undergraduate_admission/admin/cutoff.html',
                      context={'form': form,
                               'students': filtered,
                               'form2': form2})

    def post(self, request, *args, **kwargs):
        form = CutOffForm(request.GET or None)

        filtered = self.get_students_matching(request)

        form2 = ApplyStatusForm(request.POST or None)

        if form2.is_valid():
            print('valid')
            status = form2.cleaned_data.get('status')
            print(status)

        messages.success(request, _('New status has been applied to students chosen...'))
        return redirect(reverse_lazy('cut_off_point'))


class VerifyCommittee(AdminBaseView, SuccessMessageMixin, UpdateView):
    template_name = 'undergraduate_admission/admin/verify_committee.html'
    form_class = VerifyCommitteeForm
    model = User
    success_message = 'List successfully saved!!!!'

    def get_success_url(self, **kwargs):
        return reverse_lazy('verify_committee', kwargs={'pk': self.kwargs['pk']})


class StudentGenderViewNOTWORKING(AdminBaseView, SuccessMessageMixin, ModelFormSetView):
    template_name = 'undergraduate_admission/admin/student_gender.html'
    model = User
    form_class = StudentGenderForm
    extra = 0
    paginate_by = 1  # doesnt work
    success_message = _('Gender updated successfully')

    def get_queryset(self):
        sem = AdmissionSemester.get_phase1_active_semester()
        students = User.objects.filter(semester=sem,
                                       is_staff=False,
                                       is_superuser=False).order_by('date_joined')
        return students

    def get_context_data(self, **kwargs):
        context = super(StudentGenderView, self).get_context_data(**kwargs)
        context['test'] = 'test'
        print(context)
        return context

    def get_success_url(self, **kwargs):
        return reverse_lazy('student_gender')  # , kwargs={'pk': self.kwargs['pk']})


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


# class YesserDataUpdateBackup(AdminBaseView, TemplateView):
#     template_name = 'undergraduate_admission/admin/yesser_update.html'
#
#     def get_context_data(self, **kwargs):
#         context = super(YesserDataUpdateBackup, self).get_context_data(**kwargs)
#         sem = AdmissionSemester.get_phase1_active_semester()
#         students = User.objects.filter(semester=sem,
#                                        is_staff=False,
#                                        is_superuser=False)
#         context['students'] = students
#
#         return context
#
#     def get(self, request, *args, **kwargs):
#         read_file = os.path.join(BASE_DIR, 'uploaded_docs') + '/names_o.csv'
#         write_file = os.path.join(BASE_DIR, 'uploaded_docs') + '/names.csv'
#         counter = 1
#         total = 27984
#
#         with open(write_file, 'w') as csvfile2:
#             fieldnames = ['username', 'high_school_gpa', 'qudrat', 'tahsili']
#             writer = csv.DictWriter(csvfile2, fieldnames=fieldnames)
#             writer.writeheader()
#
#             with open(read_file) as csvfile:
#                 reader = csv.DictReader(csvfile)
#                 for row in reader:
#                     # time.sleep(0.09)
#                     data = get_qiyas_from_yesser(row['username'])
#                     print('%s: %s'%(counter/total * 100, data))
#                     counter = counter + 1
#                     writer.writerow({'username': row['username'],
#                                      'high_school_gpa': row['high_school_gpa'],
#                                      'qudrat': data['qudrat'],
#                                      'tahsili': data['tahsili'],
#                                      })
#
#         return super(YesserDataUpdateBackup, self).get(request)


class YesserDataUpdate(AdminBaseView, TemplateView):
    template_name = 'undergraduate_admission/admin/yesser_update.html'

    def get_context_data(self, **kwargs):
        context = super(YesserDataUpdate, self).get_context_data(**kwargs)
        sem = AdmissionSemester.get_phase1_active_semester()
        students = User.objects.filter(semester=sem,
                                       is_staff=False,
                                       is_superuser=False)
        context['students'] = students

        return context


class QiyasDataUpdate(AdminBaseView, TemplateView):
    def get(self, request, *args, **kwargs):
        special_cases_log = ''
        final_data, data = {}, {}
        gov_id = request.GET.get('gov_id', 0)
        print(gov_id)
        sem = AdmissionSemester.get_phase1_active_semester()
        print(sem)
        try:
            student = User.objects.get(semester=sem,
                                       is_staff=False,
                                       is_superuser=False,
                                       username=gov_id)

            data = merge_dicts(get_qudrat_from_yesser(gov_id),
                               get_tahsili_from_yesser(gov_id),
                               get_high_school_from_yesser(gov_id))
            print(data)

            if not data['q_error']:
                student.first_name_ar = data['FirstName']
                student.second_name_ar = data['SecondName']
                student.third_name_ar = data['ThirdName']
                student.family_name_ar = data['LastName']
                student.qudrat_score = data['qudrat']

            if not data['t_error']:
                student.tahsili_score = data['tahsili']

            if not data['hs_error']:
                student.high_school_gpa = data['high_school_gpa']
                if data['CertificationHijriYear']:
                    year = GraduationYear.get_graduation_year(data['CertificationHijriYear'])
                    """
                    this is the case of student who entered his hs year wrong
                    """
                    if year and student.high_school_graduation_year != year:
                        student.high_school_graduation_year = year
                        special_cases_log += '{%s} entered his hs year wrong and got updated<br>' % (student.username)
                        """
                        this is the case of a student who was marked as old hs but actually has recent hs in MOE
                        """
                        if data['CertificationHijriYear'] in ['2015-2016', '2016-2017'] \
                                and student.status_message == RegistrationStatusMessage.get_status_old_high_school():
                            student.status_message = RegistrationStatusMessage.get_status_applied()
                            special_cases_log += \
                                '{%s} was marked as old hs but actually has recent hs in MOE<br>' % (student.username)
                    """
                    this is the case of a student who has old hs status but he has recent hs in his application
                    """
                    if year and student.high_school_graduation_year == year and \
                                    student.status_message == RegistrationStatusMessage.get_status_old_high_school():
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
                            student.status_message = RegistrationStatusMessage.get_status_old_high_school()
                            special_cases_log += \
                                '{%s} has old hs in MOE but has a status of applied<br>' % (student.username)
                if data['Gender'] and student.gender != data['Gender']:
                    student.gender = data['Gender']
                    special_cases_log += '{%s} has his gender changed to {%s}<br>' % (student.username, data['Gender'])
                student.high_school_name = data['SchoolNameAr']
                student.high_school_province = data['AdministrativeAreaNameAr']

            student.save()

            final_data = {'status': student.status_message.status.status_ar,
                          'hs': data['high_school_gpa'],
                          'qudrat': data['qudrat'],
                          'tahsili': data['tahsili'],
                          'log': special_cases_log}

        except ObjectDoesNotExist:
            final_data = {'status': 'Not found',
                          'hs': 0.0,
                          'qudrat': 0.0,
                          'tahsili': 0.0,
                          'log': ''}

        return HttpResponse(json.dumps(final_data), content_type='application/json; charset=utf-8')
        # return HttpResponse(json_string, content_type='application/json; charset=utf-8')


def get_qudrat_from_yesser(gov_id):
    client = Client(YESSER_QIYAS_WSDL)
    data = {}
    resultQudrat = client.service.GetExamResult(gov_id, '01', '01')
    # print(resultQudrat)

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
    return data


def get_tahsili_from_yesser(gov_id):
    client = Client(YESSER_QIYAS_WSDL)
    data = {}
    resultTahsili = client.service.GetExamResult(gov_id, '02', '01')
    # print(resultTahsili)

    if not resultTahsili.ServiceError:
        data['t_error'] = 0
        data['tahsili'] = resultTahsili.GetExamResultResponseDetailObject.ExamResult.ExamResult
    else:  # no tahsili result from Qiyas
        data['t_error'] = resultTahsili.ServiceError.Code
        data['tahsili'] = 0
    return data


def get_high_school_from_yesser(gov_id):
    client = Client(YESSER_MOE_WSDL)
    data = {}
    result = client.service.GetHighSchoolCertificate(gov_id)
    # print(result)

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
    return data
