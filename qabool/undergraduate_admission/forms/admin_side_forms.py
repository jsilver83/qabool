import floppyforms.__future__ as forms
from django.utils import timezone

from undergraduate_admission.models import User, Lookup, RegistrationStatusMessage, GraduationYear
from django.utils.translation import ugettext_lazy as _, get_language


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
    class Meta:
        model = User
        fields = ['username', 'nationality', 'saudi_mother', 'student_full_name_ar', 'student_full_name_en',
                  # 'status_message',

                  'first_name_ar', 'second_name_ar', 'third_name_ar', 'family_name_ar',
                  'first_name_en', 'second_name_en', 'third_name_en', 'family_name_en',

                  'email', 'mobile', 'high_school_gpa',
                  # 'qudrat_score', 'tahsili_score',
                  'high_school_graduation_year', 'high_school_system',

                  'government_id_issue', 'government_id_expiry', 'government_id_place',
                  'passport_number', 'passport_place', 'passport_expiry',
                  'birthday', 'birthday_ah', 'birth_place',

                  'high_school_name', 'high_school_province', 'high_school_city',
                  'eligible_for_housing',

                  'high_school_certificate',
                  'personal_picture',
                  'mother_gov_id_file',
                  'saudi_mother_gov_id',
                  'birth_certificate',
                  'government_id_file',
                  'passport_file',
                  'courses_certificate',

                  'have_a_vehicle',
                  'vehicle_plate_no',
                  'vehicle_registration_file',
                  'driving_license_file',

                  'verification_documents_incomplete',
                  'verification_picture_acceptable',
                  'verification_status',
                  'verification_notes', ]

    def __init__(self, *args, **kwargs):
        super(VerifyCommitteeForm, self).__init__(*args, **kwargs)

        readonly_fields = ['username', 'nationality', 'saudi_mother', 'status_message',

                           'email', 'mobile', 'high_school_gpa', 'qudrat_score', 'tahsili_score',
                           # 'high_school_graduation_year', 'high_school_system',

                           'have_a_vehicle',
                           'vehicle_plate_no',

                           'verification_notes',
                           ]
        for field in self.fields:
            if field in readonly_fields:
                self.fields[field].disabled = True
            self.fields['verification_status'].widget = \
                forms.CheckboxSelectMultiple(choices=Lookup.get_lookup_choices('VERIFICATION_STATUS', False))
            self.fields['verification_notes'].widget = forms.Textarea(attrs={'required': ''})
            # admin.widgets.AdminTextareaWidget()


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
