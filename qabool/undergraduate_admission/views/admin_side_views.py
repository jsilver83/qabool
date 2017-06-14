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

from qabool.local_settings import YESSER_QIYAS_WSDL
from undergraduate_admission.filters import UserListFilter
from undergraduate_admission.forms.admin_side_forms import CutOffForm, VerifyCommitteeForm, ApplyStatusForm, \
    StudentGenderForm
from undergraduate_admission.models import User, AdmissionSemester
from undergraduate_admission.utils import try_parse_float


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
        client = Client(YESSER_QIYAS_WSDL)
        gov_id = request.GET.get('govid', 0)

        sem = AdmissionSemester.get_phase1_active_semester()
        try:
            student = User.objects.get(semester=sem,
                                       is_staff=False,
                                       is_superuser=False,
                                       username=gov_id)

            resultQudrat = client.service.GetExamResult(gov_id, '01', '01')
            resultTahsili = client.service.GetExamResult(gov_id, '02', '01')
            print(resultQudrat)
            print(resultTahsili)

            data = {}
            data['qudrat_before'] = student.qudrat_score
            data['tahsili_before'] = student.tahsili_score

            try:
                data['qudrat_after'] = resultQudrat.GetExamResultResponseDetailObject.ExamResult.ExamResult
            except AttributeError:  # no qudrat result from Qiyas
                data['qudrat_after'] = -1

            try:
                data['tahsili_after'] = resultTahsili.GetExamResultResponseDetailObject.ExamResult.ExamResult
            except AttributeError:  # no tahsili result from Qiyas
                data['tahsili_after'] = -1

        except ObjectDoesNotExist:
            data = {}

        return HttpResponse(json.dumps(data), content_type="application/json")
