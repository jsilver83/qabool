import floppyforms.__future__ as forms
from django.utils import timezone

from undergraduate_admission.models import User, Lookup, RegistrationStatusMessage, GraduationYear
from django.utils.translation import ugettext_lazy as _, get_language


class CutOffForm(forms.ModelForm):
    GENDER_CHOICES = (
        ('', _('Both')),
        ('M', _('Male')),
        ('F', _('Female'))
    )
    STUDENT_TYPES = (
        ('S', _('Saudi')),
        ('M', _('Saudi Mother')),
        ('N', _('Non-Saudi')),
    )
    student_type = forms.CharField(widget=forms.CheckboxSelectMultiple(choices=STUDENT_TYPES),
                                   required=False)
    # gender = forms.CharField(widget=forms.RadioSelect(choices=GENDER_CHOICES))
    # nationality = forms.IntegerField(widget=forms.Select(choices=Nationality.get_nationality_choices(), attrs={'class': 'select2'}))
    admission_total = forms.FloatField(min_value=1, max_value=100, required=False)

    class Meta:
        model = User
        fields = ['semester', 'gender', 'nationality', 'admission_total', 'student_type',
                  'high_school_graduation_year']

    def __init__(self, *args, **kwargs):
        super(CutOffForm, self).__init__()
        self.fields['gender'].widget = forms.RadioSelect(choices=self.GENDER_CHOICES)
        self.fields['gender'].required = False
        self.fields['nationality'].required = False
        self.fields['nationality'].widget.is_required = False
        self.fields['high_school_graduation_year'].widget = \
            widget = forms.CheckboxSelectMultiple(choices=
                                                  GraduationYear.get_graduation_year_choices(add_dashes=False))
        self.fields['high_school_graduation_year'].required = False


class VerifyCommitteeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'nationality', 'saudi_mother', 'student_full_name_ar', 'student_full_name_en',
                  'status_message',

                  'first_name_ar', 'second_name_ar', 'third_name_ar', 'family_name_ar',
                  'first_name_en', 'second_name_en', 'third_name_en', 'family_name_en',

                  'email', 'mobile', 'high_school_gpa', 'qudrat_score', 'tahsili_score',
                  'high_school_graduation_year', 'high_school_system',

                  'government_id_issue', 'government_id_expiry', 'government_id_place',
                  'passport_number', 'passport_place', 'passport_expiry',
                  'birthday', 'birthday_ah', 'birth_place',

                  'high_school_name', 'high_school_province', 'high_school_city',
                  'eligible_for_housing',

                  'high_school_certificate',
                  'personal_picture',
                  'mother_gov_id_file',
                  'birth_certificate',
                  'government_id_file',
                  'passport_file',
                  'courses_certificate',

                  'have_a_vehicle',
                  'vehicle_plate_no',
                  'vehicle_registration_file',
                  'driving_license_file',

                  'verification_status',
                  'verification_notes', ]

    def __init__(self, *args, **kwargs):
        super(VerifyCommitteeForm, self).__init__(*args, **kwargs)

        readonly_fields = ['username', 'nationality', 'saudi_mother', 'status_message',

                           'email', 'mobile', 'high_school_gpa', 'qudrat_score', 'tahsili_score',
                           'high_school_graduation_year', 'high_school_system',

                           'verification_notes', ]
        for field in self.fields:
            if field in readonly_fields:
                self.fields[field].disabled = True
            self.fields['verification_status'].widget = \
            forms.CheckboxSelectMultiple(choices=Lookup.get_lookup_choices('VERIFICATION_STATUS', False))
            self.fields['verification_notes'].widget = forms.Textarea(attrs={'required':''}) # admin.widgets.AdminTextareaWidget()
