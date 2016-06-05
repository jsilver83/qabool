import floppyforms.__future__ as forms
# from bootstrap3_datetime.widgets import DateTimePicker

from undergraduate_admission.models import User, Lookup
from django.utils.translation import ugettext_lazy as _, get_language


class PersonalInfoForm(forms.ModelForm):

    class Meta:
        model = User

        fields = ['first_name_ar', 'second_name_ar', 'third_name_ar', 'family_name_ar', 'first_name_en',
                  'second_name_en', 'third_name_en', 'family_name_en', 'phone', 'birthday', 'birthday_ah',
                  'government_id_issue', 'government_id_expiry', 'government_id_place',
                  'passport_number', 'passport_place', 'passport_expiry',
                  'social_status', 'employment', 'employer_name',
                  'disability_needs', 'other_needs', 'chronic_diseases',
                  'high_school_name', 'high_school_province', 'high_school_city']

        widgets = {
            # 'birthday': DateTimePicker(options={"format": "YYYY-MM-DD",
            #                                     "pickTime": False})
            'birthday': forms.DateInput(attrs={'class': 'datepicker'}),
            'birthday_ah': forms.DateInput(attrs={'placeholder': 'DD/MM/YYYY'}),
            'government_id_issue': forms.DateInput(attrs={'class': 'datepicker'}),
            'government_id_expiry': forms.DateInput(attrs={'class': 'datepicker'}),
            'passport_expiry': forms.DateInput(attrs={'class': 'datepicker'}),
            'social_status': forms.Select(choices= Lookup.get_lookup_choices('SOCIAL_STATUS')),
            'employment': forms.Select(choices= Lookup.get_lookup_choices('EMPLOYMENT_STATUS')),
            'disability_needs': forms.Select(choices= Lookup.get_lookup_choices('DISABILITY')),
            'chronic_diseases': forms.Select(choices= Lookup.get_lookup_choices('CHRONIC_DISEASES')),
        }

        # help_texts = {
        #     'username': _('National ID for Saudis, Iqama Number for non-Saudis.'),
        # }
        # initial = {'username': _('Government ID')}

    def __init__(self, *args, **kwargs):
        super(PersonalInfoForm, self).__init__(*args, **kwargs)


# class EducationInfoForm(forms.ModelForm):
#
#     class Meta:
#         model = User
#
#         fields = ['high_school_name', 'high_school_province', 'high_school_city']
#
#     def __init__(self, *args, **kwargs):
#         super(EducationInfoForm, self).__init__(*args, **kwargs)


class GuardianContactForm(forms.ModelForm):

    class Meta:
        model = User

        fields = ['guardian_name', 'guardian_government_id', 'guardian_relation', 'guardian_phone', 'guardian_mobile',
                  'guardian_email', 'guardian_po_box', 'guardian_postal_code', 'guardian_city', 'guardian_job',
                  'guardian_employer']

        widgets = {
            'guardian_relation': forms.Select(choices= Lookup.get_lookup_choices('PERSON_RELATION')),
        }

    def __init__(self, *args, **kwargs):
        super(GuardianContactForm, self).__init__(*args, **kwargs)


class RelativeContactForm(forms.ModelForm):

    class Meta:
        model = User

        fields = ['relative_name', 'relative_relation', 'relative_phone', 'relative_po_box',
                  'relative_po_stal_code', 'relative_city', 'relative_job', 'relative_employer']

        widgets = {
            'relative_relation': forms.Select(choices= Lookup.get_lookup_choices('PERSON_RELATION')),
        }

    def __init__(self, *args, **kwargs):
        super(RelativeContactForm, self).__init__(*args, **kwargs)


class DocumentsForm(forms.ModelForm):

    class Meta:
        model = User

        fields = ['personal_picture', 'high_school_certificate', 'government_id_file', 'passport_file',
                  'birth_certificate', 'mother_gov_id_file', ]

    def __init__(self, *args, **kwargs):
        super(DocumentsForm, self).__init__(*args, **kwargs)

        if self.instance.get_student_type() == 'N':
            del self.fields['mother_gov_id_file']
            del self.fields['birth_certificate']

        elif self.instance.get_student_type() == 'S':
            del self.fields['mother_gov_id_file']
            del self.fields['birth_certificate']
            del self.fields['passport_file']

        # make all fields required
        for field in self.fields:
            self.fields[field].required = True
