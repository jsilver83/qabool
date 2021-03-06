import json
import logging
import time
from datetime import datetime
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, F, Case, When, Value, CharField
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic import UpdateView, View
from zeep import Client, Settings
from zeep.transports import Transport
from zeep.wsse import UsernameToken

from undergraduate_admission.filters import AdmissionRequestListFilter
from undergraduate_admission.forms.admin_side_forms import *
from undergraduate_admission.models import AdmissionSemester, GraduationYear, RegistrationStatus
from undergraduate_admission.utils import try_parse_float, concatenate_names

logger = logging.getLogger(__name__)

YESSER_MOE_WSDL = settings.YESSER_MOE_WSDL
YESSER_MOHE_WSDL = settings.YESSER_MOHE_WSDL
YESSER_QIYAS_WSDL = settings.YESSER_QIYAS_WSDL
SMART_CARD_WSDL = settings.SMART_CARD_WSDL
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


# TODO: rework and use filters and search and add a tab that shows all
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


class VerifyStudent(StaffBaseView, SuccessMessageMixin, UpdateView):
    template_name = 'undergraduate_admission/admin/verify_committee.html'
    form_class = VerifyCommitteeForm
    model = AdmissionRequest
    success_message = _('Verification submitted successfully!!!!')

    # TODO: check if the student can be verified

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


class TransferImportView(AdminBaseView, FormView):
    template_name = 'undergraduate_admission/admin/transfer_import.html'
    form_class = TransferImportForm

    def form_valid(self, form):
        semester = get_object_or_404(AdmissionSemester, pk=form.cleaned_data.get('semester', 0))
        status_message = get_object_or_404(RegistrationStatus, pk=form.cleaned_data.get('status_message', 0))
        transfer_data = form.cleaned_data.get('transfer_data')

        users_created = 0
        requests_created = 0
        already_existing_users = []
        already_existing_requests = []
        for line in transfer_data.splitlines():
            # line = line.strip()
            if line and len(line.split()) == 4:
                student_id = line.split()[0]
                kfupm_id = line.split()[1]
                mobile = line.split()[2]
                nationality = line.split()[3]

                if User.objects.filter(username=student_id).count() == 0:
                    password = User.objects.make_random_password()
                    user = User.objects.create_user(student_id, None, password)
                    users_created += 1
                else:
                    user = User.objects.filter(username=student_id).first()
                    already_existing_users.append(user)

                admission_request, created = AdmissionRequest.objects.get_or_create(user=user,
                                                                          semester=semester)

                admission_request.kfupm_id = kfupm_id
                admission_request.nationality = nationality
                admission_request.mobile = mobile
                admission_request.status_message = status_message
                admission_request.save()

                get_student_record_serialized(admission_request,
                                              change_status=False,
                                              overwrite=True)

                if created:
                    requests_created += 1
                else:
                    already_existing_requests.append(admission_request)

        success_message = 'Import done successfully. {} new requests were created. {} new users were created.' \
            .format(requests_created, users_created)

        if already_existing_requests:
            success_message = '{} {} are already existing requests'.format(
                success_message, already_existing_requests)

        if already_existing_users:
            success_message = '{} {} are already existing users'.format(success_message, already_existing_users)

        messages.success(self.request, success_message)
        return redirect(reverse_lazy('undergraduate_admission:transfer_import'))


class SmartCardExportView(AdminBaseView, FormView):
    template_name = 'undergraduate_admission/admin/smart-card-export.html'
    form_class = SmartCardExportForm

    def form_valid(self, form, **kwargs):
        semester = get_object_or_404(AdmissionSemester, pk=form.cleaned_data.get('semester', 0))
        status_message = get_object_or_404(RegistrationStatus, pk=form.cleaned_data.get('status_message', 0))

        zeep_settings = Settings(strict=False, raw_response=False)
        client = Client(
            SMART_CARD_WSDL, transport=transport,
            wsse=UsernameToken(settings.SMART_CARD_USERNAME, settings.SMART_CARD_PASSWORD),
            settings=zeep_settings,
        )

        students_to_exported = AdmissionRequest.objects.filter(semester=semester, status_message=status_message)

        kfupm_ids_text = form.cleaned_data.get('kfupm_ids')
        if kfupm_ids_text:
            kfupm_ids = re.split(',|, | ,| |\n', kfupm_ids_text)
            kfupm_ids = [x for x in kfupm_ids if len(x)]
            students_to_exported = students_to_exported.filter(kfupm_id__in=kfupm_ids)

        total_students = students_to_exported.count()
        exported_students = []
        failed_students = []
        exported_students_count = 0

        for student in students_to_exported:
            residency_type = 'OnCampus' if student.eligible_for_housing else 'OffCampus'
            gender = 'Male' if student.gender == AdmissionRequest.Gender.MALE else 'Female'

            personal_picture_as_bytes = None
            if student.personal_picture:
                with student.personal_picture.open("rb") as image:
                    f = image.read()
                    personal_picture_as_bytes = bytearray(f)

            try:
                client.service.NewToken(
                    TokenType='Student',
                    GovID=student.user.username,
                    KfupmID=student.kfupm_id,
                    LastNameEng=student.family_name_en,
                    FirstNamesEng=student.first_name_en,
                    NameArab=student.get_student_full_name_ar(),
                    NationalityArab=student.arabic_nationality(),
                    NationalityEng=student.english_nationality(),
                    BirthDateEnglish=student.birthday,
                    BirthDateArabic=student.birthday_ah,
                    CityOfBirthEng=student.birth_place[0:34],
                    CityOfBirthArab=student.birth_place[0:34],
                    BloodTypeEng=student.blood_type,
                    OfficePhone=student.guardian_mobile,
                    PhysicalDisabled=student.is_disabled,
                    Email=student.user.email,
                    MobilePhone=student.mobile,
                    DepartmentUnitPosition='Undecided Major',
                    ResidencyType=residency_type,
                    Gender=gender,
                    StartDate=datetime.today(),
                    EndDate=None,
                    StudentCategory='Preparatory',
                    HomePhone=student.guardian_phone,
                    DependentSequenceNumber=0,
                    Photo=personal_picture_as_bytes
                )
                exported_students.append(student)
                exported_students_count += 1
            except Exception as e:
                failed_students.append({'student': student, 'error': str(e)})
                logger.exception(
                    "Something bad happened while sending student {} data to smart-card. Error: {}".format(
                        student, str(e)
                    )
                )

        success_message = '{} out of {} got exported to Smart-card server successfully'.format(
            exported_students_count, total_students
        )
        messages.success(self.request, success_message)

        context = self.get_context_data(**kwargs)
        context['exported_students'] = exported_students
        context['failed_students'] = failed_students

        return self.render_to_response(context)


class TarifiDistributeView(AdminBaseView, TemplateView):
    template_name = 'undergraduate_admission/admin/base_admin_area.html'

    def get(self, request, *args, **kwargs):
        send_sms = kwargs.get('send_sms', 0)
        semester = AdmissionSemester.get_active_semester()
        from tarifi.models import TarifiData
        summary_message = TarifiData.distribute_admission_requests_in_tarifi_slots(admission_semester=semester,
                                                                                   send_sms=send_sms)
        messages.success(self.request, summary_message)
        return super().get(request, *args, **kwargs)


class YesserDataFetchView(StaffBaseView, FormView):
    template_name = 'undergraduate_admission/admin/yesser_data_fetch.html'
    form_class = YesserDataFetchForm

    def form_valid(self, form, *args, **kwargs):
        students_government_id = form.cleaned_data.get('students_government_id')

        data = []

        for government_id in students_government_id.splitlines():
            government_id = government_id.strip()
            qudrat_data = get_qudrat_from_yesser(government_id)
            tahsili_data = get_tahsili_from_yesser(government_id)
            hs_data = get_high_school_from_yesser(government_id)

            data.append(
                [
                    government_id,
                    '{} {}'.format(qudrat_data.get('FirstName', ''), qudrat_data.get('LastName', '')),
                    qudrat_data.get('qudrat', Decimal(0.00)),
                    tahsili_data.get('tahsili', Decimal(0.00)), hs_data
                    .get('high_school_gpa', Decimal('0.00')),
                ]
            )

        if data:
            context = self.get_context_data(**kwargs)
            context['data'] = data
            messages.success(self.request, _('Data fetched successfully successfully.'))
            return self.render_to_response(context)

        messages.error(self.request, _('Data could NOT be fetched.'))
        return redirect(reverse_lazy('undergraduate_admission:yesser_data_fetch'))


# class TarifiDistributeView(AdminBaseView, FormView):
#     template_name = 'undergraduate_admission/admin/smart-card-export.html'
#     form_class = SmartCardExportForm
#
#     def form_valid(self, form, **kwargs):
#         semester = get_object_or_404(AdmissionSemester, pk=form.cleaned_data.get('semester', 0))
#         status_message = get_object_or_404(RegistrationStatus, pk=form.cleaned_data.get('status_message', 0))
#
#         students_to_distributed = AdmissionRequest.objects.filter(semester=semester, status_message=status_message)
#
#         kfupm_ids_text = form.cleaned_data.get('kfupm_ids')
#         if kfupm_ids_text:
#             kfupm_ids = re.split(',|, | ,| |\n', kfupm_ids_text)
#             kfupm_ids = [x for x in kfupm_ids if len(x)]
#             students_to_distributed = students_to_distributed.filter(kfupm_id__in=kfupm_ids)
#
#         total_students = students_to_distributed.count()
#         exported_students = []
#         failed_students = []
#         exported_students_count = 0
#
#         for student in students_to_distributed:
#             residency_type = 'OnCampus' if student.eligible_for_housing else 'OffCampus'
#             gender = 'Male' if student.gender == AdmissionRequest.Gender.MALE else 'Female'
#
#             personal_picture_as_bytes = None
#             if student.personal_picture:
#                 with student.personal_picture.open("rb") as image:
#                     f = image.read()
#                     personal_picture_as_bytes = bytearray(f)
#
#             try:
#
#                 exported_students.append(student)
#                 exported_students_count += 1
#             except Exception as e:
#                 failed_students.append({'student': student, 'error': str(e)})
#                 logger.exception(
#                     "Something bad happened while sending student {} data to smart-card. Error: {}".format(
#                         student, str(e)
#                     )
#                 )
#
#         success_message = '{} out of {} got exported to Smart-card server successfully'.format(
#             exported_students_count, total_students
#         )
#         messages.success(self.request, success_message)
#
#         context = self.get_context_data(**kwargs)
#         context['exported_students'] = exported_students
#         context['failed_students'] = failed_students
#
#         return self.render_to_response(context)


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
    except Exception as e:
        logger.exception("Something bad happened while syncing student {}. Error: {}.".format(student, str(e)))

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


def get_admission_mohe_from_yesser(gov_id):
    try:
        client = Client(YESSER_MOHE_WSDL, transport=transport)
        result = client.service.GetStudentAdmissionStatusByNationalID(gov_id, 'NationalID')

        return result.GetStudentAdmissionStatusByNationalIDResponseDetailObject.StudentAdmission[0].University.UniversityID
    except:
        pass


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
    try:
        client = Client(YESSER_MOHE_WSDL, transport=transport)
        result = client.service.GetStudentAdmissionStatusByNationalID(government_id, 'NationalID')

        file = open('fetched_from_yesser/all.csv', 'a')
        university = result.GetStudentAdmissionStatusByNationalIDResponseDetailObject.StudentAdmission[0].University.UniversityID
        file.write(
            str("%s,%s\n" % (
                government_id, university
            ))
        )
        file.close()
    except:
        pass


def operational_script(input_file, output_file):
    """
    :param input_file:  '2019_Hs_pt2.txt'
    :param output_file: 'students_data_pt2.csv'
    :return:
    """
    import csv
    with open(output_file, 'a+', newline='') as csv_file:
        students_data = csv.writer(csv_file, quoting=csv.QUOTE_MINIMAL)
        students_data.writerow(['#', 'Gov ID', 'HS', 'Qudrat', 'Tahsili', 'GPA', 'Univ'])

    counter = 1

    with open(input_file, 'r') as f:
        gov_id = f.readline().strip()
        while gov_id:
            high_school_gpa = float(get_high_school_from_yesser(gov_id).get('high_school_gpa', 0.0))
            qudrat = float(get_qudrat_from_yesser(gov_id).get('qudrat', 0.0))
            tahsili = float(get_tahsili_from_yesser(gov_id).get('tahsili', 0.0))
            gpa = (high_school_gpa * 0.20) + (qudrat * 0.30) + (tahsili * 0.50)

            if gpa > 90:
                univ = get_admission_mohe_from_yesser(gov_id)
            else:
                univ = ''

            with open(output_file, 'a+', newline='') as csv_file:
                students_data = csv.writer(csv_file, quoting=csv.QUOTE_MINIMAL)
                students_data.writerow([counter, gov_id, high_school_gpa, qudrat, tahsili, gpa, univ])

            gov_id = f.readline().strip()
            counter += 1
