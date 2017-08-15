import base64

import floppyforms.__future__ as forms
import re
from django.utils import timezone

from undergraduate_admission.models import User, Lookup, RegistrationStatusMessage, GraduationYear, AdmissionSemester
from django.utils.translation import ugettext_lazy as _, get_language

from undergraduate_admission.utils import SMS


class CutOffForm(forms.ModelForm):
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
        model = User
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


class VerifyCommitteeForm(forms.ModelForm):
    data_uri = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = User
        fields = ['username', 'nationality', 'saudi_mother',

                  'first_name_ar', 'second_name_ar', 'third_name_ar', 'family_name_ar',
                  'first_name_en', 'second_name_en', 'third_name_en', 'family_name_en',

                  'mobile', 'high_school_gpa',
                  # 'qudrat_score', 'tahsili_score',
                  'high_school_graduation_year', 'high_school_system', 'high_school_major',

                  'government_id_expiry', 'government_id_place',
                  'passport_number', 'passport_place', 'passport_expiry',
                  'birthday', 'birthday_ah', 'birth_place',

                  'high_school_name', 'high_school_province', 'high_school_city',

                  'high_school_certificate',
                  'personal_picture',
                  'mother_gov_id_file',
                  'saudi_mother_gov_id',
                  'birth_certificate',
                  'government_id_file',
                  'passport_file',
                  'courses_certificate',

                  'verification_documents_incomplete',
                  'verification_picture_acceptable',
                  'verification_status',
                  'verification_notes',
                  'data_uri',
                  ]

        widgets = {
            'birthday': forms.DateInput(attrs={'class': 'datepicker'}),
            'birthday_ah': forms.TextInput(attrs={'placeholder': 'YYYY/MM/DD', 'class': 'hijri'}),
            'government_id_expiry': forms.TextInput(attrs={'placeholder': 'YYYY/MM/DD', 'class': 'hijri'}),
            'passport_expiry': forms.DateInput(attrs={'class': 'datepicker'}),
        }

    def __init__(self, *args, **kwargs):
        super(VerifyCommitteeForm, self).__init__(*args, **kwargs)

        readonly_fields = ['username', 'nationality', 'saudi_mother', 'status_message',
                           'email', 'mobile', 'high_school_gpa', 'qudrat_score', 'tahsili_score', ]
        for field in self.fields:
            if field in readonly_fields:
                self.fields[field].disabled = True
        self.fields['username'].label = _('Government ID')
        self.fields['username'].help_text = ''
        self.fields['mobile'].help_text = ''
        self.fields['verification_notes'].widget = forms.Textarea()
        self.fields['verification_notes'].required = False
        self.fields['verification_documents_incomplete'].required = True
        self.fields['verification_picture_acceptable'].required = True
        self.fields['high_school_system'].widget = forms.Select(choices=Lookup.get_lookup_choices('HIGH_SCHOOL_TYPE'))
        self.fields['verification_status'].widget = forms.CheckboxSelectMultiple(
                choices=Lookup.get_lookup_choices('VERIFICATION_STATUS', False))

    def save(self, commit=True):
        student = super(VerifyCommitteeForm, self).save(commit=False)

        verification_documents_incomplete = self.cleaned_data.get('verification_documents_incomplete')
        verification_picture_acceptable = self.cleaned_data.get('verification_picture_acceptable')
        if (verification_documents_incomplete or verification_picture_acceptable):
            if student.student_type in ('S', 'M'):
                status = RegistrationStatusMessage.get_status_confirmed()
            else:
                status = RegistrationStatusMessage.get_status_confirmed_non_saudi()
            student.status_message = status
            student.phase2_start_date = timezone.now()
            student.phase2_end_date = timezone.datetime(day=19, month=7, year=2017, hour=13, minute=30)
        elif verification_documents_incomplete == False and verification_picture_acceptable == False \
                and student.student_type in ('S', 'M'):
            status = RegistrationStatusMessage.get_status_admitted()
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

        if commit:
            student.save()
            if (verification_documents_incomplete or verification_picture_acceptable):
                SMS.send_sms_docs_issue_message(student.mobile)
                SMS.send_sms_docs_issue_message(student.guardian_mobile)
            elif verification_documents_incomplete == False and verification_picture_acceptable == False \
                    and student.student_type in ('S', 'M'):
                SMS.send_sms_admitted(student.mobile)
                SMS.send_sms_admitted(student.guardian_mobile)
            return student
        else:
            return student


class ApplyStatusForm(forms.Form):
    status_message = forms.IntegerField(widget=forms.Select(
        choices=RegistrationStatusMessage.get_registration_status_choices()), required=True, label=_('Message Status'))


class StudentGenderForm(forms.ModelForm):
    GENDER_CHOICES = (
        ('', _('Unknown')),
        ('M', _('Male')),
        ('F', _('Female'))
    )

    class Meta:
        model = User
        fields = ['gender']

    def __init__(self, *args, **kwargs):
        super(StudentGenderForm, self).__init__(*args, **kwargs)
        self.fields['gender'].widget = forms.Select(choices=self.GENDER_CHOICES)
        self.fields['gender'].required = True

    def save(self, commit=True):
        instance = super(StudentGenderForm, self).save(commit=False)
        if instance.gender == 'F':
            reg_msg = RegistrationStatusMessage.get_status_girls()
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
            forms.Select(choices=RegistrationStatusMessage.get_registration_status_choices())

