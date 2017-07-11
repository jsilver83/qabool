import base64

import floppyforms.__future__ as forms
import re
from django.utils import timezone

from undergraduate_admission.models import User, Lookup, RegistrationStatusMessage
from django.utils.translation import ugettext_lazy as _, get_language

YES_NO_CHOICES = (
    ('True', _("Yes")),
    ('False', _("No")),
)


# to save phase 2 submit date on all phase 2 forms
class Phase2GenericForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['id', ]

    def save(self, commit=True):
        instance = super(Phase2GenericForm, self).save(commit=False)
        instance.phase2_submit_date = timezone.now()
        if commit:
            instance.save()
            return instance
        else:
            return instance


class PersonalInfoForm(Phase2GenericForm):
    YES_NO_CHOICES = (
        ('True', _("Yes")),
        ('No', _("No")),
    )

    class Meta:
        model = User

        fields = ['first_name_ar', 'second_name_ar', 'third_name_ar', 'family_name_ar', 'first_name_en',
                  'second_name_en', 'third_name_en', 'family_name_en', 'phone',
                  'high_school_name', 'high_school_province', 'high_school_city',
                  'birthday_ah', 'birthday', 'birth_place',
                  'government_id_expiry', 'government_id_place',
                  'passport_number', 'passport_place', 'passport_expiry', 'social_status',
                  'is_employed', 'employer_name',  # 'employment',
                  'blood_type',
                  'is_disabled', 'disability_needs', 'disability_needs_notes',
                  'is_diseased', 'chronic_diseases', 'chronic_diseases_notes', ]

        widgets = {
            'birthday': forms.DateInput(attrs={'class': 'datepicker'}),
            'birthday_ah': forms.TextInput(attrs={'placeholder': 'YYYY/MM/DD', 'class': 'hijri'}),
            'government_id_expiry': forms.TextInput(attrs={'placeholder': 'YYYY/MM/DD', 'class': 'hijri'}),
            'passport_expiry': forms.DateInput(attrs={'class': 'datepicker'}),
            'social_status': forms.RadioSelect(choices=Lookup.get_lookup_choices('SOCIAL_STATUS', False)),
            'employment': forms.RadioSelect(choices=Lookup.get_lookup_choices('EMPLOYMENT_STATUS', False)),
            'disability_needs': forms.CheckboxSelectMultiple(choices=Lookup.get_lookup_choices('DISABILITY', False)),
            'chronic_diseases': forms.CheckboxSelectMultiple(
                choices=Lookup.get_lookup_choices('CHRONIC_DISEASES', False)),
            'blood_type': forms.Select(choices=Lookup.get_lookup_choices('BLOOD_TYPE', add_dashes=True)),
            'is_employed': forms.RadioSelect(choices=YES_NO_CHOICES),
            'is_disabled': forms.RadioSelect(choices=YES_NO_CHOICES),
            'is_diseased': forms.RadioSelect(choices=YES_NO_CHOICES),
        }
        help_texts = {
            'phone': _('With country and area code. e.g. 966138602722'),
        }

    def clean(self):
        cleaned_data = super(PersonalInfoForm, self).clean()
        is_diseased = cleaned_data.get('is_diseased')
        chronic_diseases = cleaned_data.get('chronic_diseases')
        is_disabled = cleaned_data.get('is_disabled')
        disability_needs = cleaned_data.get('disability_needs')

        if is_diseased and not chronic_diseases:
            raise forms.ValidationError(_('Chronic diseases list can not be empty'))

        if is_disabled and not disability_needs:
            raise forms.ValidationError(_('Disability type(s) can not be empty'))

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(PersonalInfoForm, self).__init__(*args, **kwargs)

        if self.instance.student_type == 'S':
            del self.fields['passport_number']
            del self.fields['passport_place']
            del self.fields['passport_expiry']

        # make all fields required except for two fields
        for field in self.fields:
            if field not in ['second_name_en', 'third_name_en', 'is_employed', 'is_disabled', 'is_diseased',
                             'employer_name', 'disability_needs_notes',
                             'disability_needs', 'chronic_diseases', 'chronic_diseases_notes', ]:
                self.fields[field].required = True
                self.fields[field].widget.attrs.update(
                    {'required': ''}
                )


class GuardianContactForm(Phase2GenericForm):
    class Meta:
        model = User

        fields = ['guardian_name', 'guardian_government_id', 'guardian_relation', 'guardian_phone',
                  # 'guardian_mobile',
                  'guardian_email', 'guardian_po_box', 'guardian_postal_code', 'guardian_city', 'guardian_job',
                  'guardian_employer']

        widgets = {
            'guardian_relation': forms.Select(choices=Lookup.get_lookup_choices('PERSON_RELATION')),
        }

    def __init__(self, *args, **kwargs):
        super(GuardianContactForm, self).__init__(*args, **kwargs)

        # make all fields required
        for field in self.fields:
            self.fields[field].required = True


class RelativeContactForm(Phase2GenericForm):
    class Meta:
        model = User

        fields = ['relative_name', 'relative_relation', 'relative_phone', 'relative_po_box',
                  'relative_po_stal_code', 'relative_city', 'relative_job', 'relative_employer']

    def __init__(self, *args, **kwargs):
        super(RelativeContactForm, self).__init__(*args, **kwargs)

        # make all fields required
        for field in self.fields:
            self.fields[field].required = True


class VehicleInfoForm(Phase2GenericForm):
    class Meta:
        model = User
        fields = ['have_a_vehicle', 'vehicle_plate_no', 'vehicle_registration_file', 'driving_license_file', ]
        widgets = {
            'have_a_vehicle': forms.RadioSelect(choices=YES_NO_CHOICES),
        }

    def clean(self):
        cleaned_data = super(VehicleInfoForm, self).clean()
        have_a_vehicle = cleaned_data.get('have_a_vehicle')
        vehicle_plate_no = cleaned_data.get('vehicle_plate_no')
        vehicle_registration_file = cleaned_data.get('vehicle_registration_file')
        driving_license_file = cleaned_data.get('driving_license_file')

        if have_a_vehicle and not (vehicle_plate_no and vehicle_registration_file and driving_license_file):
            raise forms.ValidationError(_('Vehicle info is required.'))

        return cleaned_data


class DocumentsForm(Phase2GenericForm):
    class Meta:
        model = User

        fields = ['high_school_certificate', 'courses_certificate', 'government_id_file',
                  'mother_gov_id_file', 'passport_file', 'birth_certificate', ]

    def __init__(self, *args, **kwargs):
        super(DocumentsForm, self).__init__(*args, **kwargs)

        if self.instance.student_type == 'N':
            del self.fields['mother_gov_id_file']
            del self.fields['birth_certificate']

        elif self.instance.student_type == 'S':
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


class WithdrawalProofForm(Phase2GenericForm):
    class Meta:
        model = User

        fields = ['withdrawal_proof_letter', ]

    def __init__(self, *args, **kwargs):
        super(WithdrawalProofForm, self).__init__(*args, **kwargs)

        # make all fields required
        for field in self.fields:
            self.fields[field].required = True
            self.fields[field].help_text = \
                _('Please upload clear scanned images with good quality. Allowed formats: '
                  'jpg, jpeg, png, bmp, gif. Max Size: 2 MB')


class WithdrawalForm(forms.ModelForm):
    class Meta:
        model = User

        fields = ['withdrawal_university', 'withdrawal_reason', ]

        widgets = {
            'withdrawal_university': forms.Select(choices=Lookup.get_lookup_choices('UNIVERSITY')),
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


class PersonalPhotoForm(forms.ModelForm):
    data_uri = forms.CharField(widget=forms.HiddenInput)

    class Meta:
        model = User
        fields = ('personal_picture', 'data_uri', )
        widgets = {
            'file': forms.FileInput(attrs={
                'accept': 'image/*'
            })
        }

    def save(self):
        photo = super(PersonalPhotoForm, self).save()

        data_uri = self.cleaned_data.get('data_uri')
        img_str = re.search(r'base64,(.*)', data_uri).group(1)
        output = open(photo.personal_picture.path, 'wb')
        output.write(base64.b64decode(img_str))
        output.close()

        return photo
