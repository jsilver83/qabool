import logging
import json
import time

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, F, Case, When, Value, CharField
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic import UpdateView, View
from zeep import Client
from zeep.transports import Transport

from undergraduate_admission.filters import AdmissionRequestListFilter
from undergraduate_admission.forms.admin_side_forms import *
from undergraduate_admission.models import AdmissionSemester, GraduationYear, RegistrationStatus
from undergraduate_admission.utils import try_parse_float, concatenate_names


logger = logging.getLogger(__name__)

YESSER_MOE_WSDL = settings.YESSER_MOE_WSDL
YESSER_MOHE_WSDL = settings.YESSER_MOHE_WSDL
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
        filtered = AdmissionRequestListFilter(request.GET, queryset=AdmissionRequest.objects.all())

        filtered_with_properties = filtered.qs.select_related('semester') \
            .annotate(
            admission_percent=F('semester__high_school_gpa_weight') * F('high_school_gpa') / 100
                              + F('semester__qudrat_score_weight') * F('qudrat_score') / 100
                              + F('semester__tahsili_score_weight') * F('tahsili_score') / 100,
            student_nationality_type=Case(When(nationality='SA', then=Value('S')),
                                          When(~ Q(nationality='SA')
                                               & Q(nationality__isnull=False)
                                               & Q(saudi_mother=True),
                                               then=Value('M')),
                                          When(~ Q(nationality='SA')
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

        filtered = AdmissionRequest.objects.none().order_by('id')
        if request.GET:
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
        filtered = AdmissionRequest.objects.filter(pk__in=self.get_students_matching(request))
        form2 = ApplyStatusForm(request.POST or None)

        if form2.is_valid():
            try:
                status = RegistrationStatus.objects.get(pk=form2.cleaned_data.get('status_message'))
                records_updated = filtered.update(status_message=status)
                students_count = filtered.count()
                messages.success(request, _('New status has been applied to %(count)d of %(all)d students chosen...')
                                 % ({'count': records_updated,
                                     'all': students_count}))
            except ObjectDoesNotExist:
                messages.error(request, _('Error in updating status...'))

        return redirect('undergraduate_admission:cut_off_point')


class DistributeStudentsOnVerifiersView(AdminBaseView, View):
    def get_students_matching(self, request):
        selected_student_types = request.GET.getlist('student_type', [])
        reassign = request.GET.get('reassign', False)
        if reassign:
            filtered = AdmissionRequestListFilter(request.GET,
                                                  queryset=AdmissionRequest.objects.all())
        else:
            filtered = AdmissionRequestListFilter(request.GET,
                                                  queryset=AdmissionRequest.objects.filter(
                                                      verification_committee_member__isnull=True))

        filtered_with_properties = filtered.qs.select_related('semester') \
            .annotate(
            admission_percent=F('semester__high_school_gpa_weight') * F('high_school_gpa') / 100
                              + F('semester__qudrat_score_weight') * F('qudrat_score') / 100
                              + F('semester__tahsili_score_weight') * F('tahsili_score') / 100,
            student_nationality_type=Case(When(nationality='SA', then=Value('S')),
                                          When(~ Q(nationality='SA')
                                               & Q(nationality__isnull=False)
                                               & Q(saudi_mother=True),
                                               then=Value('M')),
                                          When(~ Q(nationality='SA')
                                               & Q(nationality__isnull=False)
                                               & (Q(saudi_mother=False) | Q(saudi_mother__isnull=True)),
                                               then=Value('N')),
                                          default=Value('N/A'),
                                          output_field=CharField())) \
            .order_by('-admission_percent')

        if selected_student_types:
            filtered_with_properties = filtered_with_properties.filter(
                student_nationality_type__in=selected_student_types)

        return filtered_with_properties

    def get(self, request, *args, **kwargs):
        form = DistributeForm(request.GET or None)
        filtered = AdmissionRequest.objects.none().order_by('id')
        if request.GET:
            filtered = self.get_students_matching(request)

        form2 = SelectCommitteeMemberForm()
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
                      template_name='undergraduate_admission/admin/distribute_committee.html',
                      context={'form': form,
                               'students': page_obj,
                               'students_count': len(filtered),
                               'form2': form2,
                               'show_detailed_results': show_detailed_results})

    def post(self, request, *args, **kwargs):
        filtered = AdmissionRequest.objects.filter(pk__in=self.get_students_matching(request))
        form2 = SelectCommitteeMemberForm(request.POST or None)

        if form2.is_valid():
            try:
                members = request.POST.getlist('members', [])
                counter = 0
                for student in filtered:
                    student.verification_committee_member = members[counter]
                    student.save()
                    if counter < len(members) - 1:
                        counter += 1
                    else:
                        counter = 0

                messages.success(request, _('%(count)d students were distributed amongst following members %(all)s ...')
                                 % ({'count': len(filtered),
                                     'all': members}))
            except ObjectDoesNotExist:
                messages.error(request, _('Error in updating status...'))

        return redirect('undergraduate_admission:distribute_committee')


class BaseVerifyList(StaffBaseView, ListView):
    template_name = 'undergraduate_admission/admin/verify_list.html'
    model = AdmissionRequest
    context_object_name = 'students'
    paginate_by = 25

    def get_queryset(self):
        logged_in_username = self.request.user.username
        status = [RegistrationStatus.get_status_confirmed(),
                  RegistrationStatus.get_status_confirmed_non_saudi()]
        semester = AdmissionSemester.get_active_semester()

        if self.request.user.is_superuser:
            students_to_verified = AdmissionRequest.objects.filter(
                semester=semester)
        else:
            students_to_verified = AdmissionRequest.objects.filter(
                status_message__in=status,
                semester=semester,
                verification_committee_member=logged_in_username)

        return students_to_verified.order_by('-phase2_re_upload_date', '-phase2_submit_date')


class VerifyListNew(BaseVerifyList):

    def get_queryset(self):
        return super().get_queryset().filter(
            Q(verification_issues=None),
            phase2_re_upload_date__isnull=True, )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'new'
        return context

    def get_success_url(self, **kwargs):
        return reverse_lazy('undergraduate_admission:verify_list_new')


class VerifyListPendingWithStudent(BaseVerifyList):

    def get_queryset(self):
        return super().get_queryset().filter(~Q(verification_issues=None),
                                             phase2_re_upload_date__isnull=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'pending'
        return context

    def get_success_url(self, **kwargs):
        return reverse_lazy('undergraduate_admission:verify_list_with_student')


class VerifyListCorrectedByStudent(BaseVerifyList):

    def get_queryset(self):
        return super().get_queryset().filter(~Q(verification_issues=None),
                                             phase2_re_upload_date__isnull=False)

    def get_context_data(self, **kwargs):
        context = super(VerifyListCorrectedByStudent, self).get_context_data(**kwargs)
        context['active_menu'] = 'corrected'
        return context

    def get_success_url(self, **kwargs):
        return reverse_lazy('undergraduate_admission:verify_list_corrected_by_student')


# class VerifyList(StaffBaseView, ListView):
#     template_name = 'undergraduate_admission/admin/verify_list.html'
#     model = AdmissionRequest
#     context_object_name = 'students'
#     paginate_by = 25
#
#     def get_queryset(self):
#         logged_in_username = self.request.user.username
#         status = [RegistrationStatus.get_status_confirmed(),
#                   RegistrationStatus.get_status_confirmed_non_saudi()]
#         semester = AdmissionSemester.get_active_semester()
#         if self.request.user.is_superuser:
#             students_to_verified = AdmissionRequest.objects.filter(
#                 # status_message__in=status,
#                 semester=semester) \
#                 .order_by('-phase2_submit_date')
#         else:
#             students_to_verified = AdmissionRequest.objects.filter(
#                 Q(verification_issues=None),
#                 phase2_re_upload_date__isnull=True,
#                 status_message__in=status,
#                 semester=semester,
#                 verification_committee_member=logged_in_username) \
#                 .order_by('-phase2_submit_date')
#         return students_to_verified
#
#     def get_context_data(self, **kwargs):
#         context = super(VerifyList, self).get_context_data(**kwargs)
#         context['active_menu'] = 'new'
#         return context


class VerifyStudent(StaffBaseView, SuccessMessageMixin, UpdateView):
    template_name = 'undergraduate_admission/admin/verify_committee.html'
    form_class = VerifyCommitteeForm
    model = AdmissionRequest
    success_message = _('Verification submitted successfully!!!!')

    def get_success_url(self, **kwargs):
        return reverse_lazy('undergraduate_admission:verify_list_new')


class YesserDataUpdate(AdminBaseView, TemplateView):
    template_name = 'undergraduate_admission/admin/yesser_update.html'

    def get_context_data(self, **kwargs):
        context = super(YesserDataUpdate, self).get_context_data(**kwargs)
        sem = AdmissionSemester.get_active_semester()
        students = AdmissionRequest.objects.filter(semester=sem)
        context['students_count'] = students.count()

        return context

    def get(self, request, *args, **kwargs):
        manual_update = self.kwargs.get('manual_update', 1)
        overwrite_update = self.kwargs.get('overwrite_update', 0)

        if manual_update:
            sem = AdmissionSemester.get_active_semester()
            students = AdmissionRequest.objects.filter(semester=sem)
            for student in students:
                time.sleep(0.3)
                get_student_record_serialized(student, change_status=True, overwrite=overwrite_update)

            return redirect(reverse_lazy('undergraduate_admission:verify_list_new'))

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
        students = AdmissionRequest.objects.filter(semester=sem)
        paginator = Paginator(students, 25)
        try:
            student = paginator.page(page).object_list[0]

            serialized_obj = get_student_record_serialized(student)
        except PageNotAnInteger:
            pass
        except EmptyPage:
            pass
        return HttpResponse(json.dumps(serialized_obj), content_type='application/json; charset=utf-8')


class SendMassSMSView(AdminBaseView, FormView):
    template_name = 'undergraduate_admission/admin/send_sms_notification.html'
    form_class = SendMassSMSForm

    def form_valid(self, form):
        students_criteria = form.cleaned_data
        print(students_criteria)


def get_student_record_serialized(student, change_status=False, overwrite=False):
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

        qudrat_data = None
        if overwrite or (not overwrite and student.yesser_qudrat_data_dump is None):
            qudrat_data = get_qudrat_from_yesser(student.government_id)

        tahsili_data = None
        if overwrite or (not overwrite and student.yesser_tahsili_data_dump is None):
            tahsili_data = get_tahsili_from_yesser(student.government_id)

        hs_data = None
        if overwrite or (not overwrite and student.yesser_high_school_data_dump is None):
            hs_data = get_high_school_from_yesser(student.government_id)

        final_data['status_before'] = student.status_message

        final_data['qudrat_before'] = student.qudrat_score
        if qudrat_data and not qudrat_data['q_error']:
            changed = True

            student.yesser_qudrat_data_dump = 'Fetched On %s<br>%s' % (timezone.now(),
                                                                       qudrat_data['all_data'],)

            if qudrat_data['FirstName'] != '-':
                student.first_name_ar = qudrat_data['FirstName']
            if qudrat_data['SecondName'] != '-':
                student.second_name_ar = qudrat_data['SecondName']
            if qudrat_data['ThirdName'] != '-':
                student.third_name_ar = qudrat_data['ThirdName']
            if qudrat_data['LastName'] != '-':
                student.family_name_ar = qudrat_data['LastName']

            student.qudrat_score = qudrat_data['qudrat']

        final_data['tahsili_before'] = student.tahsili_score
        if tahsili_data and not tahsili_data['t_error']:
            changed = True

            student.yesser_tahsili_data_dump = 'Fetched On %s<br>%s' % (timezone.now(),
                                                                        tahsili_data['all_data'],)

            student.tahsili_score = tahsili_data['tahsili']

        final_data['high_school_gpa_before'] = student.high_school_gpa
        if hs_data and not hs_data['hs_error']:
            changed = True

            student.yesser_high_school_data_dump = 'Fetched On %s<br>%s' % (timezone.now(),
                                                                            hs_data['all_data'],)

            student.high_school_gpa = hs_data['high_school_gpa']

            if hs_data['CertificationHijriYear']:
                year = GraduationYear.get_graduation_year(hs_data['CertificationHijriYear'])

                if year:
                    """
                    this is the case of a student who entered his hs year wrong
                    """
                    if student.high_school_graduation_year != year:
                        student.high_school_graduation_year = year
                        special_cases_log += '{%s} entered his hs year wrong and got updated<br>' % student.government_id

                    """
                    this is the case of a student who was marked as old hs but actually has recent hs in MOE
                    """
                    if year.type in [GraduationYear.GraduationYearTypes.CURRENT_YEAR,
                                     GraduationYear.GraduationYearTypes.LAST_YEAR] \
                            and student.status_message == RegistrationStatus.get_status_old_high_school():
                        if change_status:
                            if student.nationality != 'SA' and not student.saudi_mother:
                                student.status_message = RegistrationStatus.get_status_applied_non_saudi()
                            else:
                                student.status_message = RegistrationStatus.get_status_applied()
                        special_cases_log += \
                            '{%s} was marked as old hs but actually has recent hs in MOE<br>' % student.government_id
                    """
                    this is the case of a student who was marked as applied but actually has old hs in MOE
                    """
                    if year.type == GraduationYear.GraduationYearTypes.OLD_HS \
                            and student.status_message in [RegistrationStatus.get_status_applied(),
                                                           RegistrationStatus.get_status_applied_non_saudi()]:
                        if change_status:
                            student.status_message = RegistrationStatus.get_status_old_high_school()
                        special_cases_log += \
                            '{%s} was marked as applied but he actually has old hs in MOE<br>' % student.government_id
                else:
                    student.high_school_graduation_year = GraduationYear.get_other_graduation_year()

                    if student.status_message != RegistrationStatus.get_status_old_high_school() and change_status:
                        student.status_message = RegistrationStatus.get_status_old_high_school()
                    special_cases_log += \
                        '{%s} was marked as old hs<br>' % student.government_id
                    """
                    this is the case of a student who has old hs year that is not included in the system
                    """

                """
                this a case of a student with no CertificationHijriYear from yesser
                """
            else:
                student.high_school_graduation_year = GraduationYear.get_other_graduation_year()

                if student.status_message != RegistrationStatus.get_status_old_high_school() and change_status:
                    student.status_message = RegistrationStatus.get_status_old_high_school()

                special_cases_log += \
                    '{%s} has no graduation year in yesser and so he was marked as old HS<br>' % student.government_id

            if hs_data['Gender']:
                student.gender = hs_data['Gender']
                if hs_data['Gender'] == 'F':
                    special_cases_log += '{%s} has his gender changed to {%s}<br>' % (student.government_id,
                                                                                      hs_data['Gender'])
                    if change_status:
                        student.status_message = RegistrationStatus.get_status_girls()

            if hs_data['StudentNameEn']:
                # hs_data['StudentNameEn'] = 'Test name please'

                student.first_name_en = ''
                student.second_name_en = ''
                student.third_name_en = ''
                student.family_name_en = ''

                # remove all hyphen beforehand
                hs_data['StudentNameEn'] = hs_data['StudentNameEn'].replace('-', '')

                english_name_split = hs_data['StudentNameEn'].split()

                if english_name_split:
                    student.first_name_en = english_name_split[0]
                    if len(english_name_split) == 2:
                        student.family_name_en = english_name_split[1]
                    if len(english_name_split) == 3:
                        student.second_name_en = english_name_split[1]
                        student.family_name_en = english_name_split[2]
                    if len(english_name_split) > 3:
                        student.second_name_en = english_name_split[1]
                        student.third_name_en = english_name_split[2]
                        student.family_name_en = \
                            concatenate_names(*english_name_split[3:])

            student.government_id_type = hs_data['MoeIdentifierTypeDesc']
            student.birthday = hs_data['GregorianDate']
            student.birthday_ah = hs_data['HijriDate']
            student.high_school_id = hs_data['SchoolID']
            student.high_school_name = hs_data['SchoolNameAr']
            student.high_school_name_en = hs_data['SchoolNameEn']
            student.high_school_province_code = hs_data['EducationAreaCode']
            student.high_school_province = hs_data['EducationAreaNameAr']
            student.high_school_province_en = hs_data['EducationAreaNameEn']
            student.high_school_city_code = hs_data['AdministrativeAreaCode']
            student.high_school_city = hs_data['AdministrativeAreaNameAr']
            student.high_school_city_en = hs_data['AdministrativeAreaNameEn']
            student.high_school_major_code = hs_data['MajorCode']
            student.high_school_major_name = hs_data['MajorTypeAr']
            student.high_school_major_name_en = hs_data['MajorTypeEn']

        if changed:
            student.save()

        final_data['changed'] = changed
        final_data['gov_id'] = student.government_id
        final_data['status'] = student.status_message
        final_data['high_school_gpa'] = student.high_school_gpa
        final_data['qudrat'] = student.qudrat_score
        final_data['tahsili'] = student.tahsili_score
        final_data['log'] = ''  # special_cases_log
        final_data['error'] = False
    except:
        logger.exception("Something bad happened while syncing student %".format(student))
        pass

    return final_data


def get_qudrat_from_yesser(gov_id):
    data = {}
    try:
        client = Client(YESSER_QIYAS_WSDL, transport=transport)
        resultQudrat = client.service.GetExamResult(gov_id, '01', '01')

        if not resultQudrat.ServiceError:
            data['q_error'] = 0
            data['all_data'] = resultQudrat
            data['qudrat'] = resultQudrat.GetExamResultResponseDetailObject.ExamResult.ExamResult
            data['FirstName'] = resultQudrat.GetExamResultResponseDetailObject.ApplicantName.PersonNameBody.FirstName
            data['SecondName'] = resultQudrat.GetExamResultResponseDetailObject.ApplicantName.PersonNameBody.SecondName
            data['ThirdName'] = resultQudrat.GetExamResultResponseDetailObject.ApplicantName.PersonNameBody.ThirdName
            data['LastName'] = resultQudrat.GetExamResultResponseDetailObject.ApplicantName.PersonNameBody.LastName
        else:  # no qudrat result from Qiyas
            data['q_error'] = resultQudrat.ServiceError.Code
            data['all_data'] = ''
            data['qudrat'] = 0
            data['FirstName'] = ''
            data['SecondName'] = ''
            data['ThirdName'] = ''
            data['LastName'] = ''
    except:
        logger.exception("Something bad happened while fetching qudrat data for student %".format(gov_id))

        data['q_error'] = 'general error'  # Client request message schema validation failure'
        data['all_data'] = ''
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

        if not resultTahsili.ServiceError:
            data['t_error'] = 0
            data['all_data'] = resultTahsili
            data['tahsili'] = resultTahsili.GetExamResultResponseDetailObject.ExamResult.ExamResult
        else:  # no tahsili result from Qiyas
            data['t_error'] = resultTahsili.ServiceError.Code
            data['all_data'] = ''
            data['tahsili'] = 0
    except:
        logger.exception("Something bad happened while fetching tahsili data for student %".format(gov_id))

        data['t_error'] = 'general error'
        data['all_data'] = ''
        data['tahsili'] = 0
    return data


def get_high_school_from_yesser(gov_id):
    data = {}
    try:
        client = Client(YESSER_MOE_WSDL, transport=transport)
        result = client.service.GetHighSchoolCertificate(gov_id)

        if not result.ServiceError:
            data['hs_error'] = 0
            data['all_data'] = result
            data['high_school_gpa'] = result.getHighSchoolCertificateResponseDetailObject. \
                CertificationDetails.GPA
            data['MoeIdentifierTypeDesc'] = result.getHighSchoolCertificateResponseDetailObject. \
                StudentBasicInfo.MoeIdentifierTypeDesc
            data['CertificationHijriYear'] = result.getHighSchoolCertificateResponseDetailObject. \
                CertificationDetails.CertificationHijriYear
            data['Gender'] = result.getHighSchoolCertificateResponseDetailObject.StudentBasicInfo.Gender
            data['StudentNameEn'] = result.getHighSchoolCertificateResponseDetailObject.StudentBasicInfo.StudentNameEn.PersonFullName
            data['SchoolID'] = result.getHighSchoolCertificateResponseDetailObject.SchoolInfo.SchoolID
            data['SchoolNameAr'] = result.getHighSchoolCertificateResponseDetailObject. \
                SchoolInfo.SchoolNameAr
            data['SchoolNameEn'] = result.getHighSchoolCertificateResponseDetailObject. \
                SchoolInfo.SchoolNameEn
            data['EducationAreaCode'] = result.getHighSchoolCertificateResponseDetailObject. \
                SchoolInfo.EducationAreaCode
            data['EducationAreaNameAr'] = result.getHighSchoolCertificateResponseDetailObject. \
                SchoolInfo.EducationAreaNameAr
            data['EducationAreaNameEn'] = result.getHighSchoolCertificateResponseDetailObject. \
                SchoolInfo.EducationAreaNameEn
            data['AdministrativeAreaCode'] = result.getHighSchoolCertificateResponseDetailObject. \
                SchoolInfo.AdministrativeAreaCode
            data['AdministrativeAreaNameAr'] = result.getHighSchoolCertificateResponseDetailObject. \
                SchoolInfo.AdministrativeAreaNameAr
            data['AdministrativeAreaNameEn'] = result.getHighSchoolCertificateResponseDetailObject. \
                SchoolInfo.AdministrativeAreaNameEn
            data['MajorCode'] = result.getHighSchoolCertificateResponseDetailObject. \
                CertificationDetails.MajorCode
            data['MajorTypeAr'] = result.getHighSchoolCertificateResponseDetailObject. \
                CertificationDetails.MajorTypeAr
            data['MajorTypeEn'] = result.getHighSchoolCertificateResponseDetailObject. \
                CertificationDetails.MajorTypeEn
            data['GregorianDate'] = result.getHighSchoolCertificateResponseDetailObject.StudentBasicInfo.DateOfBirth. \
                GregorianDate
            data['HijriDate'] = result.getHighSchoolCertificateResponseDetailObject.StudentBasicInfo.DateOfBirth. \
                HijriDate
        else:
            data['hs_error'] = result.ServiceError.Code
            data['all_data'] = ''
            data['high_school_gpa'] = 0
            data['MoeIdentifierTypeDesc'] = ''
            data['CertificationHijriYear'] = ''
            data['Gender'] = ''
            data['StudentNameEn'] = ''
            data['SchoolID'] = ''
            data['SchoolNameAr'] = ''
            data['SchoolNameEn'] = ''
            data['EducationAreaCode'] = ''
            data['EducationAreaNameAr'] = ''
            data['EducationAreaNameEn'] = ''
            data['AdministrativeAreaCode'] = ''
            data['AdministrativeAreaNameAr'] = ''
            data['AdministrativeAreaNameEn'] = ''
            data['MajorCode'] = ''
            data['MajorTypeAr'] = ''
            data['MajorTypeEn'] = ''
    except:
        logger.exception("Something bad happened while fetching high school data for student %".format(gov_id))

        data['hs_error'] = 'general error'
        data['all_data'] = ''
        data['high_school_gpa'] = 0
        data['MoeIdentifierTypeDesc'] = ''
        data['CertificationHijriYear'] = ''
        data['Gender'] = ''
        data['StudentNameEn'] = ''
        data['SchoolID'] = ''
        data['SchoolNameAr'] = ''
        data['SchoolNameEn'] = ''
        data['EducationAreaCode'] = ''
        data['EducationAreaNameAr'] = ''
        data['EducationAreaNameEn'] = ''
        data['AdministrativeAreaCode'] = ''
        data['AdministrativeAreaNameAr'] = ''
        data['AdministrativeAreaNameEn'] = ''
        data['MajorCode'] = ''
        data['MajorTypeAr'] = ''
        data['MajorTypeEn'] = ''
    return data


####################################
####### OPERATIONAL CODE ###########
####################################
def fetch_all_moe_from_yesser():
    students = AdmissionRequest.objects.all()  # .order_by('-id')[:50]

    for student in students:
        time.sleep(0.2)
        fetch_moe_data_from_yesser_and_write_to_file(student.government_id)


def fetch_moe_data_from_yesser_and_write_to_file(government_id):
    try:
        client = Client(YESSER_MOE_WSDL, transport=transport)

        result = client.service.GetHighSchoolCertificate(government_id)
        if not result.ServiceError:
            file = open('fetched_from_yesser/%s.txt' % (government_id,), 'w')
            file.write(str(result))
            file.close()
    except:
        pass


def fetch_all_mohe_from_yesser():
    students = AdmissionRequest.objects.all()  # .order_by('-id')[:1000]

    for student in students:
        time.sleep(1)
        # print('========')
        fetch_mohe_data_from_yesser_and_write_to_file(student.government_id)


def fetch_mohe_data_from_yesser_and_write_to_file(government_id):
    # print(government_id)
    try:
        client = Client(YESSER_MOHE_WSDL, transport=transport)
        result = client.service.GetStudentAdmissionStatusByNationalID(government_id, 'NationalID')

        file = open('fetched_from_yesser/all.csv', 'a')
        # print(result.GetStudentAdmissionStatusByNationalIDResponseDetailObject.StudentAdmission[0].University.UniversityID)
        file.write(
            str("%s,%s\n" % (
                government_id,
                result.GetStudentAdmissionStatusByNationalIDResponseDetailObject.StudentAdmission[
                    0].University.UniversityID
            ))
        )
        file.close()
    except:
        pass
