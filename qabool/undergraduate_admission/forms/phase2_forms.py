import base64
import re

from captcha.fields import CaptchaField
from django import forms
from django.contrib.auth import password_validation
from django.utils.translation import ugettext_lazy as _

from shared_app.base_forms import BaseCrispyForm
from undergraduate_admission.utils import parse_non_standard_numerals
from ..models import *
from ..validators import get_accepted_extensions

# from captcha.fields import ReCaptchaField

YES_NO_CHOICES = (
    ('True', _("Yes")),
    ('False', _("No")),
)


# to save phase 2 submit date on all phase 2 forms
class Phase2GenericForm(BaseCrispyForm, forms.ModelForm):
    class Meta:
        model = AdmissionRequest
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
    class Meta:
        model = AdmissionRequest
        fields = ['phone',
                  'high_school_name', 'high_school_province', 'high_school_city',
                  'birthday_ah', 'birthday', 'birth_place',
                  'government_id_expiry', 'government_id_place',
                  'passport_number', 'passport_place', 'passport_expiry', 'social_status',
                  'is_employed', 'employer_name',
                  'bank_name', 'bank_account', 'bank_account_identification_file',
                  'blood_type',
                  'is_disabled', 'disability_needs', 'disability_needs_notes',
                  'is_diseased', 'chronic_diseases', 'chronic_diseases_notes', ]

        widgets = {
            'birthday': forms.DateInput(attrs={'class': 'datepicker'}),
            'birthday_ah': forms.TextInput(attrs={'placeholder': 'YYYY/MM/DD', 'class': 'hijri'}),
            'government_id_expiry': forms.TextInput(attrs={'placeholder': 'YYYY/MM/DD', 'class': 'hijri'}),
            'passport_expiry': forms.DateInput(attrs={'class': 'datepicker'}),
            'is_employed': forms.RadioSelect(choices=YES_NO_CHOICES),
            'is_disabled': forms.RadioSelect(choices=YES_NO_CHOICES),
            'is_diseased': forms.RadioSelect(choices=YES_NO_CHOICES),
        }
        help_texts = {
            'phone': _('With country and area code. e.g. 966138602722'),
            'bank_account_identification_file': _('Allowed formats: pdf, jpg, jpeg, png, bmp, gif. Max Size: 2 MB'),
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
                             'bank_name', 'bank_account', 'bank_account_identification_file',
                             'disability_needs', 'chronic_diseases', 'chronic_diseases_notes', ]:
                self.fields[field].required = True
                self.fields[field].widget.attrs.update(
                    {'required': '', }
                )

            if field in ['student_full_name_ar', 'student_full_name_en',
                         'first_name_ar', 'second_name_ar', 'third_name_ar', 'family_name_ar',
                         'first_name_en', 'second_name_en', 'third_name_en', 'family_name_en',
                         'high_school_name', 'high_school_province', 'high_school_city', ]:
                self.fields[field].widget.attrs.update(
                    {'class': 'updateOnce', }
                )

        self.fields['social_status'].widget = forms.RadioSelect(
            choices=Lookup.get_lookup_choices(Lookup.LookupTypes.SOCIAL_STATUS, False))
        self.fields['disability_needs'].widget = forms.CheckboxSelectMultiple(
            choices=Lookup.get_lookup_choices(Lookup.LookupTypes.DISABILITY, False))
        self.fields['chronic_diseases'].widget = forms.CheckboxSelectMultiple(
            choices=Lookup.get_lookup_choices(Lookup.LookupTypes.CHRONIC_DISEASES, False))
        self.fields['blood_type'].widget = forms.Select(
            choices=Lookup.get_lookup_choices(Lookup.LookupTypes.BLOOD_TYPE, add_dashes=True))
        self.fields['bank_name'].widget = forms.Select(
            choices=Lookup.get_lookup_choices(Lookup.LookupTypes.BANK_NAMES, add_dashes=True))


class GuardianContactForm(Phase2GenericForm):
    class Meta:
        model = AdmissionRequest

        fields = ['guardian_name', 'guardian_government_id', 'guardian_relation', 'guardian_phone',
                  # 'guardian_mobile',
                  'guardian_email', 'guardian_po_box', 'guardian_postal_code', 'guardian_city', 'guardian_job',
                  'guardian_employer']

    def __init__(self, *args, **kwargs):
        super(GuardianContactForm, self).__init__(*args, **kwargs)

        # make all fields required
        for field in self.fields:
            self.fields[field].required = True

        self.fields['guardian_relation'].widget = forms.Select(
            choices=Lookup.get_lookup_choices(Lookup.LookupTypes.PERSON_RELATION)
        )


class RelativeContactForm(Phase2GenericForm):
    class Meta:
        model = AdmissionRequest

        fields = ['relative_name', 'relative_relation', 'relative_phone', 'relative_po_box',
                  'relative_postal_code', 'relative_city', 'relative_job', 'relative_employer']

    def __init__(self, *args, **kwargs):
        super(RelativeContactForm, self).__init__(*args, **kwargs)

        # make all fields required
        for field in self.fields:
            self.fields[field].required = True


class DocumentsForm(Phase2GenericForm):
    class Meta:
        model = AdmissionRequest

        fields = ['high_school_certificate', 'courses_certificate', 'government_id_file',
                  'mother_gov_id_file', 'passport_file', 'birth_certificate',
                  'have_a_vehicle', 'vehicle_owner', 'vehicle_plate_no',
                  'vehicle_registration_file', 'driving_license_file', ]
        widgets = {
            'have_a_vehicle': forms.RadioSelect(choices=YES_NO_CHOICES),
        }

    def __init__(self, *args, **kwargs):
        super(DocumentsForm, self).__init__(*args, **kwargs)
        try:
            self.fields['vehicle_owner'].widget = \
                forms.RadioSelect(choices=Lookup.get_lookup_choices(Lookup.LookupTypes.VEHICLE_OWNER, False))
        except:  # for the subclass form MissingDocumentsForm that doesnt have vehicle_owner field
            pass

        if self.instance.student_type == 'N':
            del self.fields['mother_gov_id_file']
            del self.fields['birth_certificate']

        elif self.instance.student_type == 'S':
            del self.fields['mother_gov_id_file']
            del self.fields['birth_certificate']
            del self.fields['passport_file']

        for field in self.fields:
            if field not in ['courses_certificate', 'have_a_vehicle', 'vehicle_owner', 'vehicle_plate_no',
                             'vehicle_registration_file', 'driving_license_file', ]:
                self.fields[field].required = True

            if field in ['high_school_certificate', 'courses_certificate', 'government_id_file',
                         'mother_gov_id_file', 'passport_file', 'birth_certificate',
                         'vehicle_registration_file', 'driving_license_file', ]:
                self.fields[field].widget.attrs.update({'accept': get_accepted_extensions('FILE')})

    def clean(self):
        cleaned_data = super().clean()
        have_a_vehicle = cleaned_data.get('have_a_vehicle')
        vehicle_owner = cleaned_data.get('vehicle_owner')
        vehicle_plate_no = cleaned_data.get('vehicle_plate_no')
        vehicle_registration_file = cleaned_data.get('vehicle_registration_file')
        driving_license_file = cleaned_data.get('driving_license_file')

        if have_a_vehicle and not (vehicle_owner and vehicle_plate_no and vehicle_registration_file
                                   and driving_license_file):
            raise forms.ValidationError(_('Vehicle info is required.'))

        return cleaned_data


class MissingDocumentsForm(DocumentsForm):
    class Meta:
        model = AdmissionRequest
        fields = ['high_school_certificate', 'courses_certificate', 'government_id_file',
                  'mother_gov_id_file', 'passport_file', 'birth_certificate',
                  'bank_account_identification_file',
                  'vehicle_registration_file', 'driving_license_file', ]

    def __init__(self, *args, **kwargs):
        super(MissingDocumentsForm, self).__init__(*args, **kwargs)
        self.fields['bank_account_identification_file'].required = False
        have_a_vehicle = self.instance.have_a_vehicle
        if not have_a_vehicle:
            del self.fields['vehicle_registration_file']
            del self.fields['driving_license_file']

        fields_to_be_removed = []
        for field in self.fields:
            if field not in list(self.instance.verification_issues.all().values_list('related_field', flat=True)):
                fields_to_be_removed.append(field)

        for field_to_be_deleted in fields_to_be_removed:
            del self.fields[field_to_be_deleted]

        for field in self.fields:
            self.initial[field] = None

    def clean(self):
        # dont call the clean in the super class since it does vehicle validation that is unneeded here
        pass


class WithdrawalProofForm(Phase2GenericForm):
    class Meta:
        model = AdmissionRequest

        fields = ['withdrawal_proof_letter', ]

    def __init__(self, *args, **kwargs):
        super(WithdrawalProofForm, self).__init__(*args, **kwargs)

        # make all fields required
        for field in self.fields:
            self.fields[field].required = True
            self.fields[field].help_text = \
                _('Please upload clear scanned images with good quality. Allowed formats: '
                  'jpg, jpeg, png, bmp, gif. Max Size: 2 MB')


class WithdrawalForm(BaseCrispyForm, forms.ModelForm):
    class Meta:
        model = AdmissionRequest

        fields = ['withdrawal_university', 'withdrawal_reason', ]

        widgets = {
            'withdrawal_reason': forms.Textarea,
        }

    def __init__(self, *args, **kwargs):
        super(WithdrawalForm, self).__init__(*args, **kwargs)

        # make all fields required
        for field in self.fields:
            self.fields[field].required = True

        self.fields['withdrawal_university'].widget = forms.Select(
            choices=Lookup.get_lookup_choices(Lookup.LookupTypes.UNIVERSITY)
        )

    def save(self, commit=True):
        instance = super(WithdrawalForm, self).save(commit=False)
        instance.withdrawal_date = timezone.now()
        reg_msg = RegistrationStatus.get_status_withdrawn()
        instance.status_message = reg_msg
        if commit and reg_msg:
            instance.save()
            return instance
        else:
            return instance


class PersonalPhotoForm(BaseCrispyForm, forms.ModelForm):
    data_uri = forms.CharField(widget=forms.HiddenInput)

    class Meta:
        model = AdmissionRequest
        fields = ('personal_picture', 'data_uri',)
        widgets = {
            'file': forms.FileInput(attrs={
                'accept': 'image/*'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['personal_picture'].widget.attrs.update({'accept': get_accepted_extensions('IMAGE')})

        self.initial['personal_picture'] = None

    def save(self, commit=True):
        photo = super(PersonalPhotoForm, self).save(commit)

        data_uri = self.cleaned_data.get('data_uri')
        img_str = re.search(r'base64,(.*)', data_uri).group(1)
        output = open(photo.personal_picture.path, 'wb')
        output.write(base64.b64decode(img_str))
        output.close()

        return photo


class TransferForm(BaseCrispyForm, forms.Form):
    username = forms.CharField(
        label=_('Government ID'),
        max_length=13,
        # min_length=7,
        help_text=_(
            'National ID for Saudis, Iqama Number for non-Saudis. e.g. 1xxxxxxxxx or 2xxxxxxxxx.'),
    )
    kfupm_id = forms.IntegerField(
        label=_('KFUPM ID'),
        required=True,
        help_text=_('Enter the ID given to you by KFUPM'),
    )

    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput,
        help_text=password_validation.password_validators_help_text_html(),
    )

    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput,
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    student_notes = forms.CharField(max_length=500, label=_('Student Notes'), required=False,
                                    widget=forms.Textarea)

    field_order = ['username', 'kfupm_id', 'password1', 'password2', 'student_notes']

    def __init__(self, *args, **kwargs):
        super(TransferForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

            if field not in ['student_notes', ]:
                self.fields[field].required = True
                self.fields[field].widget.attrs.update({'required': ''})

            if field in ['username', 'kfupm_id', ]:
                self.fields[field].widget.attrs.update({'class': 'nocopy'})

        self.fields['kfupm_id'].validators = [
            MinValueValidator(
                limit_value=1,
                message=_('Invalid KFUPM ID')
            )]

        if not settings.DISABLE_CAPTCHA:
            # self.fields['captcha'] = ReCaptchaField(label=_('Captcha'), attrs={'lang': translation.get_language()})
            self.fields['captcha'] = CaptchaField(label=_('Confirmation Code'))

    def clean(self):
        cleaned_data = super(TransferForm, self).clean()
        username = parse_non_standard_numerals(cleaned_data.get("username"))
        kfupm_id = cleaned_data.get('kfupm_id', 0)
        active_semester = AdmissionSemester.get_active_semester()
        status_message = RegistrationStatus.get_status_partially_admitted_transfer()

        try:
            student = AdmissionRequest.objects.get(user__username=username,
                                                   kfupm_id=kfupm_id,
                                                   semester=active_semester,
                                                   status_message=status_message)
            self.admission_request = student
            password1 = self.cleaned_data.get('password1')
            password2 = self.cleaned_data.get('password2')
            if password1 and password2:
                if password1 != password2:
                    raise forms.ValidationError(
                        _('Password Mismatch'),
                        code='password_mismatch',
                    )
            password_validation.validate_password(password2, self.admission_request.user)
        except ObjectDoesNotExist:
            raise forms.ValidationError(
                _('You are not eligible for a transfer to KFUPM'),
                code='not_a_transfer_student',
            )

        return cleaned_data

    def clean_username(self):
        username = parse_non_standard_numerals(self.cleaned_data.get("username"))
        return username


class CompareNamesForm(Phase2GenericForm):
    class Meta:
        model = AdmissionRequest
        fields = ['student_full_name_ar', 'student_full_name_en', ]
