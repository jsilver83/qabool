import floppyforms.__future__ as forms
from django.utils import timezone

from undergraduate_admission.models import User, Lookup, RegistrationStatusMessage
from django.utils.translation import ugettext_lazy as _, get_language


class PersonalInfoForm(forms.ModelForm):
    YES_NO_CHOICES = (
        ('True', _("Yes")),
        ('No', _("No")),
    )

    # is_employed = forms.BooleanField(
    #     label=_('Are You Employed?'),
    #     required=True,
    #     widget=forms.RadioSelect(choices=YES_NO_CHOICES),
    #     help_text=_('It is required that applicant be unemployed to be full-time. In case you are currently employed,'
    #                 ' you need to bring clearance from your employer.')
    # )
    # is_disabled = forms.BooleanField(
    #     label=_('Do you have any disabilities?'),
    #     help_text=_('This will let us help you better and will not affect your acceptance chances.'),
    #     required=True,
    #     widget=forms.RadioSelect(choices= YES_NO_CHOICES),
    # )
    # is_diseased = forms.BooleanField(
    #     label=_('Do you have any chronic diseases?'),
    #     help_text=_('This will let us help you better and will not affect your acceptance chances.'),
    #     required=True,
    #     widget=forms.RadioSelect(choices= YES_NO_CHOICES),
    # )

    class Meta:
        model = User

        fields = ['first_name_ar', 'second_name_ar', 'third_name_ar', 'family_name_ar', 'first_name_en',
                  'second_name_en', 'third_name_en', 'family_name_en', 'phone',
                  'high_school_name', 'high_school_province', 'high_school_city',
                  'birthday_ah', 'birthday', 'birth_place',
                  'government_id_expiry', 'government_id_place',
                  'passport_number', 'passport_place', 'passport_expiry', 'social_status',
                  'is_employed', 'employer_name', # 'employment',
                  'blood_type',
                  'is_disabled', 'disability_needs', 'disability_needs_notes',
                  'is_diseased', 'chronic_diseases', 'chronic_diseases_notes',]

        YES_NO_CHOICES = (
            ('True', _("Yes")),
            ('False', _("No")),
        )

        widgets = {
            'birthday': forms.DateInput(attrs={'class': 'datepicker'}),
            'birthday_ah': forms.TextInput(attrs={'placeholder': 'YYYY/MM/DD', 'class': 'hijri'}),
            'government_id_expiry': forms.TextInput(attrs={'placeholder': 'YYYY/MM/DD', 'class': 'hijri'}),
            'passport_expiry': forms.DateInput(attrs={'class': 'datepicker'}),
            'social_status': forms.RadioSelect(choices=Lookup.get_lookup_choices('SOCIAL_STATUS', False)),
            'employment': forms.RadioSelect(choices=Lookup.get_lookup_choices('EMPLOYMENT_STATUS', False)),
            'disability_needs': forms.CheckboxSelectMultiple(choices=Lookup.get_lookup_choices('DISABILITY', False)),
            'chronic_diseases': forms.CheckboxSelectMultiple(choices=Lookup.get_lookup_choices('CHRONIC_DISEASES', False)),
            'blood_type': forms.Select(choices=Lookup.get_lookup_choices('BLOOD_TYPE', False)),
            'is_employed': forms.RadioSelect(choices=YES_NO_CHOICES),
            'is_disabled': forms.RadioSelect(choices=YES_NO_CHOICES),
            'is_diseased': forms.RadioSelect(choices=YES_NO_CHOICES),
        }
        help_texts = {
            'phone': _('With country and area code. e.g. 966138602722'),
        }

    def __init__(self, *args, **kwargs):
        super(PersonalInfoForm, self).__init__(*args, **kwargs)

        print(self.instance.chronic_diseases)
        self.fields['chronic_diseases'].queryset = (c[0] for c in self.instance.chronic_diseases)

        if self.instance.get_student_type() == 'S':
            del self.fields['passport_number']
            del self.fields['passport_place']
            del self.fields['passport_expiry']

        # make all fields required except for two fields
        for field in self.fields:
            if field not in ['second_name_en', 'third_name_en', 'is_employed', 'employer_name', 'disability_needs_notes',
                             'disability_needs', 'chronic_diseases', 'chronic_diseases_notes', ]:
                self.fields[field].required = True
                self.fields[field].widget.attrs.update(
                    {'required': ''}
                )

            if field == 'birthday_ah':
                if self.instance.birthday_ah:
                    self.fields[field].widget.attrs.update(
                        {'class': 'updateOnce',}
                    )
                else:
                    self.fields[field].widget.attrs.update(
                        {'class': 'hijri updateOnce',}
                    )
            elif field == 'birthday':
                if self.instance.birthday:
                    self.fields[field].widget.attrs.update(
                        {'class': 'updateOnce',}
                    )
                else:
                    self.fields[field].widget.attrs.update(
                        {'class': 'datepicker updateOnce',}
                    )
            elif field in ['first_name_ar', 'second_name_ar', 'third_name_ar', 'family_name_ar', 'first_name_en',
                           'second_name_en', 'third_name_en', 'family_name_en', 'high_school_name',
                           'high_school_province']:
                self.fields[field].widget.attrs.update(
                    {'class': 'updateOnce',}
                )


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

        fields = ['guardian_name', 'guardian_government_id', 'guardian_relation', 'guardian_phone', # 'guardian_mobile',
                  'guardian_email', 'guardian_po_box', 'guardian_postal_code', 'guardian_city', 'guardian_job',
                  'guardian_employer']

        widgets = {
            'guardian_relation': forms.Select(choices= Lookup.get_lookup_choices('PERSON_RELATION')),
        }

    def __init__(self, *args, **kwargs):
        super(GuardianContactForm, self).__init__(*args, **kwargs)

        # make all fields required
        for field in self.fields:
            self.fields[field].required = True


class RelativeContactForm(forms.ModelForm):

    class Meta:
        model = User

        fields = ['relative_name', 'relative_relation', 'relative_phone', 'relative_po_box',
                  'relative_po_stal_code', 'relative_city', 'relative_job', 'relative_employer']

        # widgets = {
        #     'relative_relation': forms.Select(choices= Lookup.get_lookup_choices('PERSON_RELATION')),
        # }

    def __init__(self, *args, **kwargs):
        super(RelativeContactForm, self).__init__(*args, **kwargs)

        # make all fields required
        for field in self.fields:
            self.fields[field].required = True


class DocumentsForm(forms.ModelForm):

    class Meta:
        model = User

        fields = ['personal_picture', 'high_school_certificate', 'government_id_file', 'courses_certificate',
                  'mother_gov_id_file', 'passport_file', 'birth_certificate', ]

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
            # self.fields[field].help_text = \
            #     _('Please upload clear scanned images with good quality. Allowed formats: '
            #       'pdf, jpg, jpeg, png, bmp, gif. Max Size: 2 MB')

        self.fields['courses_certificate'].required = False


class WithdrawalForm(forms.ModelForm):

    class Meta:
        model = User

        fields = ['withdrawal_university', 'withdrawal_reason', ]

        widgets = {
            'withdrawal_university': forms.Select(choices= Lookup.get_lookup_choices('UNIVERSITY')),
        }

    def __init__(self, *args, **kwargs):
        super(WithdrawalForm, self).__init__(*args, **kwargs)

        # make all fields required
        for field in self.fields:
            self.fields[field].required = True

    def save(self, commit=True):
        instance = super(WithdrawalForm, self).save(commit=False)
        instance.withdrawal_date = timezone.now()
        reg_msg = RegistrationStatusMessage.get_status_withdrawn()
        instance.status_message = reg_msg
        if commit and reg_msg:
            instance.save()
            return instance
        else:
            return instance
