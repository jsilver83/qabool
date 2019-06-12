import base64

from django import forms
import re

from django.contrib.auth import get_user_model
from django.forms import CheckboxSelectMultiple
from django.utils import timezone

from shared_app.base_forms import BaseCrispyForm
from shared_app.fields import GroupedModelMultipleChoiceField
from .phase2_forms import YES_NO_CHOICES
from ..models import *
from django.utils.translation import ugettext_lazy as _, get_language

from undergraduate_admission.utils import SMS


User = get_user_model()


class CutOffForm(BaseCrispyForm, forms.ModelForm):
    GENDER_CHOICES = (
        ('', _('Unknown')),
        ('M', _('Male')),
        ('F', _('Female'))
    )
    STUDENT_TYPES = (
        ('S', _('Saudi')),
        ('M', _('Saudi Mother')),
        ('N', _('Non-Saudi')),
    )
    OPERAND_TYPES = (
        ('GTE', _('Greater Than Or Equal')),
        ('LT', _('Less Than')),
    )
    student_type = forms.CharField(widget=forms.CheckboxSelectMultiple(choices=STUDENT_TYPES),
                                   required=False, label=_('Student Type'))
    selected_high_school_graduation_year = \
        forms.CharField(widget=forms.CheckboxSelectMultiple(choices=
        GraduationYear.get_graduation_year_choices(
            add_dashes=False)),
            required=False, label=_('Graduation Year'))
    admission_total = forms.FloatField(min_value=1, max_value=100, required=False, label=_('Admission Total'))
    admission_total_operand = forms.CharField(widget=forms.RadioSelect(choices=OPERAND_TYPES),
                                              required=False, label=_('Admission Total Operand'))
    show_detailed_results = forms.BooleanField(required=False, label=_('Show Detailed Results'))

    class Meta:
        model = AdmissionRequest
        fields = ['semester', 'gender', 'student_type', 'nationality', 'status_message', 'admission_total',
                  'admission_total_operand', 'selected_high_school_graduation_year']

    def __init__(self, *args, **kwargs):
        super(CutOffForm, self).__init__(*args, **kwargs)
        self.fields['gender'].widget = forms.RadioSelect(choices=self.GENDER_CHOICES)
        self.fields['gender'].required = False
        self.fields['nationality'].required = False
        self.fields['nationality'].widget.is_required = False
        # self.fields['high_school_graduation_year'].widget = \
        #     forms.CheckboxSelectMultiple(choices=
        # GraduationYear.get_graduation_year_choices(add_dashes=False))
        # self.fields['high_school_graduation_year'].required = False


class DistributeForm(BaseCrispyForm, forms.ModelForm):
    STUDENT_TYPES = (
        ('S', _('Saudi')),
        ('M', _('Saudi Mother')),
        ('N', _('Non-Saudi')),
    )
    student_type = forms.CharField(widget=forms.CheckboxSelectMultiple(choices=STUDENT_TYPES),
                                   required=False, label=_('Student Type'))
    reassign = forms.BooleanField(required=False, label=_('Reassign?'),
                                  help_text=_('Reassign students who has already been assigned to a committee member?'))
    show_detailed_results = forms.BooleanField(required=False, label=_('Show Detailed Results'))

    class Meta:
        model = AdmissionRequest
        fields = ['semester', 'student_type', 'status_message']

    def __init__(self, *args, **kwargs):
        super(DistributeForm, self).__init__(*args, **kwargs)


# TODO: To be reworked along with the view
class SelectCommitteeMemberForm(BaseCrispyForm, forms.Form):
    members = forms.CharField(required=False, label=_('Select Member(s)'))

    def __init__(self, *args, **kwargs):
        super(SelectCommitteeMemberForm, self).__init__(*args, **kwargs)
        choices = User.objects.filter(is_staff=True,
                                      groups__name__in=['Verifying Committee', ])

        ch = [(o.username, o.username) for o in choices]
        self.fields['members'].widget = forms.CheckboxSelectMultiple(choices=ch)


class VerifyCommitteeForm(BaseCrispyForm, forms.ModelForm):
    data_uri = forms.CharField(widget=forms.HiddenInput, required=False)
    verification_issues = GroupedModelMultipleChoiceField(
        queryset=VerificationIssues.objects.all(),
        choices_groupby='get_related_field_display',
        widget=CheckboxSelectMultiple,
        required=False,
        label=_('Verification Issues')
    )

    class Meta:
        model = AdmissionRequest
        fields = ['nationality', 'saudi_mother',

                  'first_name_ar', 'second_name_ar', 'third_name_ar', 'family_name_ar',
                  'first_name_en', 'second_name_en', 'third_name_en', 'family_name_en',

                  # 'student_full_name_en', 'student_full_name_ar',

                  'mobile', 'high_school_gpa',
                  'high_school_graduation_year', 'high_school_system',

                  'government_id_expiry', 'government_id_place',
                  'passport_number', 'passport_place', 'passport_expiry',
                  'birthday', 'birthday_ah', 'birth_place',

                  'high_school_name', 'high_school_major_name', 'high_school_province', 'high_school_city',

                  'high_school_certificate',
                  'personal_picture',
                  'mother_gov_id_file',
                  'saudi_mother_gov_id',
                  'birth_certificate',
                  'government_id_file',
                  'passport_file',
                  'courses_certificate',

                  # 'have_a_vehicle', 'vehicle_owner', 'vehicle_plate_no',
                  # 'vehicle_registration_file', 'driving_license_file',

                  # 'bank_name',
                  # 'bank_account',
                  # 'bank_account_identification_file',

                  'verification_issues',
                  'verification_notes',
                  'data_uri',
                  ]

        widgets = {
            'birthday': forms.DateInput(attrs={'class': 'datepicker'}),
            'birthday_ah': forms.TextInput(attrs={'placeholder': 'YYYY/MM/DD', 'class': 'hijri'}),
            'government_id_expiry': forms.TextInput(attrs={'placeholder': 'YYYY/MM/DD', 'class': 'hijri'}),
            'passport_expiry': forms.DateInput(attrs={'class': 'datepicker'}),
            # 'have_a_vehicle': forms.RadioSelect(choices=YES_NO_CHOICES),
        }

    def __init__(self, *args, **kwargs):
        super(VerifyCommitteeForm, self).__init__(*args, **kwargs)

        readonly_fields = ['nationality', 'saudi_mother', 'status_message',
                           'email', 'mobile', 'high_school_gpa', 'qudrat_score', 'tahsili_score',
                           'bank_name', 'bank_account', 'bank_account_identification_file',
                           ]
        for field in self.fields:
            if field in readonly_fields:
                self.fields[field].disabled = True
        self.fields['mobile'].help_text = ''
        self.fields['verification_notes'].widget = forms.Textarea()
        self.fields['verification_notes'].required = False

        for field in self.fields:
            if field in ['first_name_ar', 'second_name_ar', 'third_name_ar', 'family_name_ar', ]:
                self.fields[field].widget.attrs.update({'class': 'n-ar'})
            elif field in ['first_name_en', 'second_name_en', 'third_name_en', 'family_name_en', ]:
                self.fields[field].widget.attrs.update({'class': 'n-en'})

        # self.fields['vehicle_owner'].widget = forms.Select(choices=Lookup.get_lookup_choices('VEHICLE_OWNER'))

    def save(self, commit=True):
        student = super(VerifyCommitteeForm, self).save()

        verification_issues = self.cleaned_data.get('verification_issues')
        if verification_issues:
            if student.student_type in ('S', 'M'):
                status = RegistrationStatus.get_status_confirmed()
            else:
                status = RegistrationStatus.get_status_confirmed_non_saudi()
            student.status_message = status
            student.phase2_start_date = timezone.now()
            student.phase2_end_date = timezone.now() + timezone.timedelta(days=1)
            student.phase2_re_upload_date = None
        else:
            if student.student_type in ('S', 'M'):
                status = RegistrationStatus.get_status_admitted()
                student.status_message = status
            else:
                status = RegistrationStatus.get_status_admitted_non_saudi()
                student.status_message = status

        try:
            data_uri = self.cleaned_data.get('data_uri')
            if data_uri:
                img_str = re.search(r'base64,(.*)', data_uri).group(1)
                output = open(student.personal_picture.path, 'wb')
                output.write(base64.b64decode(img_str))
                output.close()
        except ValueError:
            pass

        student.save()
        if verification_issues:
            # pass
            SMS.send_sms_docs_issue_message(student.mobile)
            SMS.send_sms_docs_issue_message(student.guardian_mobile)
        elif verification_issues is None and student.student_type in ('S', 'M'):
            # pass
            SMS.send_sms_admitted(student.mobile)
            SMS.send_sms_admitted(student.guardian_mobile)

        return student


class ApplyStatusForm(BaseCrispyForm, forms.Form):
    status_message = forms.IntegerField(widget=forms.Select(
        choices=RegistrationStatus.get_registration_status_choices()), required=True, label=_('Message Status'))


class StudentGenderForm(forms.ModelForm):
    GENDER_CHOICES = (
        ('', _('Unknown')),
        ('M', _('Male')),
        ('F', _('Female'))
    )

    class Meta:
        model = AdmissionRequest
        fields = ['gender']

    def __init__(self, *args, **kwargs):
        super(StudentGenderForm, self).__init__(*args, **kwargs)
        self.fields['gender'].widget = forms.Select(choices=self.GENDER_CHOICES)
        self.fields['gender'].required = True

    def save(self, commit=True):
        instance = super(StudentGenderForm, self).save(commit=False)
        if instance.gender == 'F':
            reg_msg = RegistrationStatus.get_status_girls()
            instance.status_message = reg_msg
        if commit:
            instance.save()
            return instance
        else:
            return instance


class SendMassSMSForm(forms.Form):
    semester = forms.IntegerField(required=True, label=_('Admission Semester'))
    status_message = forms.IntegerField(required=True, label=_('Message Status'))
    eligible_for_housing = forms.NullBooleanField(label=_('Eligible For Housing'))
    sms_message = forms.CharField(widget=forms.Textarea,
                                  max_length=70,
                                  required=True, label=_('SMS Message To Be Sent'))

    def __init__(self, *args, **kwargs):
        super(SendMassSMSForm, self).__init__(*args, **kwargs)
        self.fields['semester'].widget = forms.Select(choices=AdmissionSemester.get_semesters_choices())
        self.fields['status_message'].widget = \
            forms.Select(choices=RegistrationStatus.get_registration_status_choices())
