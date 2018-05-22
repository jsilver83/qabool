import re

from captcha.fields import CaptchaField
# from captcha.fields import ReCaptchaFieldfrom django.utils import translation

from django.utils.translation import ugettext_lazy as _, get_language
import floppyforms.__future__ as forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator

from django.conf import settings
from undergraduate_admission.forms.general_forms import BaseContactForm
from undergraduate_admission.models import AdmissionSemester, DeniedStudent, User, Lookup, Nationality, GraduationYear
from undergraduate_admission.utils import parse_non_standard_numerals, add_validators_to_arabic_and_english_names


class BaseAgreementForm(forms.Form):
    agree1 = forms.BooleanField(label=_('I have read all of the above terms and conditions'))

    def clean_agree1(self):
        agree1 = self.cleaned_data.get("agree1")

        if not agree1:
            raise forms.ValidationError(
                message=_('You have to check this box')
            )


class AgreementForm(BaseAgreementForm):
    agree2 = forms.BooleanField(label=_('I accept all the above terms and conditions'))

    def clean_agree2(self):
        agree2 = self.cleaned_data.get("agree2")

        if not agree2:
            raise forms.ValidationError(
                message=_('You have to check this box')
            )


class Phase1UserEditForm(BaseContactForm):
    class Meta(BaseContactForm.Meta):
        fields = ['first_name_ar', 'second_name_ar', 'third_name_ar', 'family_name_ar',
                  'first_name_en', 'second_name_en', 'third_name_en', 'family_name_en',
                  'mobile', 'mobile2', 'email', 'email2', 'high_school_system',
                  'high_school_gpa_student_entry', 'student_notes']

    def __init__(self, *args, **kwargs):
        super(Phase1UserEditForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            if field not in ['student_notes', 'third_name_ar', 'second_name_en', 'third_name_en']:
                self.fields[field].required = True
                self.fields[field].widget.attrs.update({'required': ''})

        add_validators_to_arabic_and_english_names(self.fields)

        self.fields['high_school_system'].widget = forms.Select(choices=Lookup.get_lookup_choices('HIGH_SCHOOL_TYPE'))


class RegistrationForm(UserCreationForm):
    UserCreationForm.error_messages.update(
        {
            'email_mismatch': _("The two email fields didn't match."),
            'govid_mismatch': _("The two government ID fields didn't match."),
            'mobile_mismatch': _("The two mobile fields didn't match."),
            'govid_denied': _("You have been denied from applying for the following reason(s): "),
            'email_not_unique': _("The Email entered is associated with another applicant. "
                                  "Please use a different Email"),
            'mobile_not_unique': _("The Mobile entered is associated with another applicant. "
                                   "Please use a different Mobile"),
            'govid_invalid': _("You have entered an invalid Government ID"),
            'guardian_mobile_match': _("You have entered the guardian mobile same as your own mobile"),
            'no_saudi_mother_gov_id': _("You have entered the mother to be Saudi but you did NOT enter her Saudi"
                                        " Government ID")
        }
    )

    email2 = forms.EmailField(
        label=_('Email Address Confirmation'),
        required=True,
        help_text=_('Enter the same email address as before, for verification'),
        widget=forms.EmailInput(attrs={'class': 'nocopy'})
    )
    username = forms.CharField(
        label=_('Government ID'),
        max_length=13,
        # min_length=7,
        help_text=_(
            'National ID for Saudis, Iqama Number for non-Saudis. e.g. 1xxxxxxxxx or 2xxxxxxxxx.'),
    )
    username2 = forms.CharField(
        label=_('Government ID Confirmation'),
        max_length=13,
        # min_length=7,
        required=True,
        help_text=_('Enter the same government ID as before, for verification'),
        widget=forms.TextInput(attrs={'class': 'nocopy'})
    )
    mobile2 = forms.CharField(
        label=_('Mobile Confirmation'),
        max_length=12,
        required=True,
        help_text=_('Enter the same mobile number as before, for verification'),
        widget=forms.TextInput(attrs={'class': 'nocopy'})
    )

    GENDER_CHOICES = (
        ('M', _('Male')),
        ('F', _('Female'))
    )

    gender = forms.CharField(
        label=_('Gender'),
        help_text=_('Only male students can apply'),
        initial='M',
        disabled=True,
        widget=forms.Select(choices=GENDER_CHOICES),
    )

    class Meta:
        model = User
        fields = ['first_name_ar', 'second_name_ar', 'third_name_ar', 'family_name_ar',
                  'first_name_en', 'second_name_en', 'third_name_en', 'family_name_en',
                  'gender',
                  'nationality', 'username', 'username2', 'mobile', 'mobile2',
                  'saudi_mother', 'saudi_mother_gov_id',
                  'email', 'email2', 'guardian_mobile', 'high_school_graduation_year', 'high_school_system',
                  'high_school_gpa_student_entry',
                  'password1', 'password2', 'student_notes']

        SAUDI_MOTHER_CHOICES = (
            ('', "---"),
            (True, _("Yes")),
            (False, _("No")),
        )

        widgets = {
            'saudi_mother': forms.Select(choices=SAUDI_MOTHER_CHOICES),
        }

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

            if field not in ['student_notes', 'third_name_ar', 'second_name_en', 'third_name_en',
                             'gender', 'saudi_mother_gov_id']:
                self.fields[field].required = True
                self.fields[field].widget.attrs.update({'required': ''})

            if field in ['username2', 'email2', 'mobile2']:
                self.fields[field].widget.attrs.update({'class': 'nocopy'})

        add_validators_to_arabic_and_english_names(self.fields)

        self.fields['nationality'].widget.attrs['class'] = 'select2 form-control'
        self.fields['mobile'].widget.attrs['placeholder'] = '9665xxxxxxxx'

        self.fields['high_school_system'].widget = forms.Select(choices=Lookup.get_lookup_choices('HIGH_SCHOOL_TYPE'))
        self.fields['saudi_mother_gov_id'].validators = [
            RegexValidator(
                '^\d{9,11}$',
                message=UserCreationForm.error_messages['govid_invalid']
            )]

        self.fields['password1'].help_text = _('Minimum length is 8. Use both numbers and characters.')
        self.fields['password2'].help_text = _('Enter the same password as before, for verification')
        self.fields['high_school_graduation_year'].queryset = GraduationYear.objects.filter(show=True)

        if not settings.DISABLE_CAPTCHA:
            # self.fields['captcha'] = ReCaptchaField(label=_('Captcha'), attrs={'lang': translation.get_language()})
            self.fields['captcha'] = CaptchaField(label=_('Confirmation Code'))

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        username1 = parse_non_standard_numerals(cleaned_data.get("username"))
        denial = DeniedStudent.check_if_student_is_denied(username1)

        if denial:
            raise forms.ValidationError(
                self.error_messages['govid_denied'] + denial,
                code='govid_denied',
                )

        is_saudi = 'Saudi' in cleaned_data.get('nationality').nationality_en

        if is_saudi:
            match = re.match(r'^\d{9,11}$', str(username1))
        else:
            match = re.match(r'^\d{7,13}$', str(username1))

        if not match:
            raise forms.ValidationError(
                UserCreationForm.error_messages['govid_invalid'],
                code='govid_invalid',
                )

    def clean_username(self):
        username = parse_non_standard_numerals(self.cleaned_data.get("username"))
        return username

    def clean_username2(self):
        username1 = parse_non_standard_numerals(self.cleaned_data.get("username"))
        username2 = parse_non_standard_numerals(self.cleaned_data.get("username2"))
        if username1 and username2 and username1 != username2:
            raise forms.ValidationError(
                self.error_messages['govid_mismatch'],
                code='govid_mismatch',
            )
        return username2

    def clean_email(self):
        email = self.cleaned_data.get("email")
        semester = AdmissionSemester.get_phase1_active_semester()
        found = User.objects.filter(email=email, semester=semester)
        if email and found:
            raise forms.ValidationError(
                self.error_messages['email_not_unique'],
                code='email_not_unique',
            )
        return email

    def clean_email2(self):
        email1 = self.cleaned_data.get("email")
        email2 = self.cleaned_data.get("email2")
        if email1 and email2 and email1 != email2:
            raise forms.ValidationError(
                self.error_messages['email_mismatch'],
                code='email_mismatch',
            )
        return email2

    def clean_mobile(self):
        mobile = parse_non_standard_numerals(self.cleaned_data.get("mobile"))
        semester = AdmissionSemester.get_phase1_active_semester()
        found = User.objects.filter(mobile=mobile, semester=semester)
        if mobile and found:
            raise forms.ValidationError(
                self.error_messages['mobile_not_unique'],
                code='mobile_not_unique',
            )
        return mobile

    def clean_mobile2(self):
        mobile1 = parse_non_standard_numerals(self.cleaned_data.get("mobile"))
        mobile2 = parse_non_standard_numerals(self.cleaned_data.get("mobile2"))
        if mobile1 and mobile2 and mobile1 != mobile2:
            raise forms.ValidationError(
                self.error_messages['mobile_mismatch'],
                code='mobile_mismatch',
            )
        return mobile2

    def clean_guardian_mobile(self):
        mobile1 = parse_non_standard_numerals(self.cleaned_data.get("mobile"))
        mobile2 = parse_non_standard_numerals(self.cleaned_data.get("guardian_mobile"))
        if mobile1 and mobile2 and mobile1 == mobile2:
            raise forms.ValidationError(
                self.error_messages['guardian_mobile_match'],
                code='guardian_mobile_match',
            )
        return mobile2

    def clean_saudi_mother_gov_id(self):
        saudi_mother = self.cleaned_data.get("saudi_mother")
        saudi_mother_gov_id = self.cleaned_data.get("saudi_mother_gov_id")
        if saudi_mother:
            if saudi_mother_gov_id:
                saudi_mother_gov_id = parse_non_standard_numerals(saudi_mother_gov_id)
            else:
                raise forms.ValidationError(
                    self.error_messages['no_saudi_mother_gov_id'],
                    code='no_saudi_mother_gov_id',
                )
        return saudi_mother_gov_id
