import re

from captcha.fields import CaptchaField
from django.contrib.auth import get_user_model, password_validation

from django.utils.translation import ugettext_lazy as _
from django import forms
from django.contrib.auth.forms import UserCreationForm

from undergraduate_admission.forms.general_forms import BaseContactForm
from ..models import *
from undergraduate_admission.utils import parse_non_standard_numerals, add_validators_to_arabic_and_english_names


User = get_user_model()


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


class RegistrationForm(BaseContactForm, forms.ModelForm):

    username = forms.CharField(
        label=_('Government ID'),
        max_length=13,
        help_text=_(
            'National ID for Saudis, Iqama Number for non-Saudis. e.g. 1xxxxxxxxx or 2xxxxxxxxx.'),
    )
    username2 = forms.CharField(
        label=_('Government ID Confirmation'),
        max_length=13,
        required=True,
        help_text=_('Enter the same government ID as before, for verification'),
        widget=forms.TextInput(attrs={'class': 'nocopy'})
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
        model = AdmissionRequest
        fields = ['student_full_name_ar', 'student_full_name_en',
                  # 'first_name_ar', 'second_name_ar', 'third_name_ar', 'family_name_ar',
                  # 'first_name_en', 'second_name_en', 'third_name_en', 'family_name_en',
                  'gender',
                  'nationality', 'saudi_mother', 'saudi_mother_gov_id', 'username', 'username2', 'mobile', 'mobile2',
                  'email', 'email2', 'guardian_mobile', 'high_school_graduation_year', 'high_school_system',
                  'high_school_certificate', 'courses_certificate', 'high_school_gpa_student_entry',
                  'password1', 'password2', 'student_notes']

        SAUDI_MOTHER_CHOICES = (
            # ('', "---"),
            (True, _("Yes")),
            (False, _("No")),
        )

        widgets = {
            'saudi_mother': forms.RadioSelect(choices=SAUDI_MOTHER_CHOICES),
        }

        labels = {
            'courses_certificate': _('High School Transcript'),
        }

        help_text_for_uploads = _("""<ol>
        <li>Please upload clear scanned images with good quality.</li>
        <li>Allowed formats: pdf, jpg, jpeg, png, bmp, gif.</li>
        <li>Mobile-taken pictures will not be accepted.</li>
        </ol>""")

        help_texts = {
            'high_school_certificate': help_text_for_uploads,
            'courses_certificate': help_text_for_uploads,
        }

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

        BaseContactForm.error_messages.update({
            'password_mismatch': _("The two password fields didn't match."),
            'govid_mismatch': _("The two government ID fields didn't match."),
            'govid_denied': _("You have been denied from applying for the following reason(s): "),
            'govid_invalid': _("You have entered an invalid Government ID"),
            'guardian_mobile_match': _("You have entered the guardian mobile same as your own mobile"),
            'saudi_mother_gov_id': _("You have entered the mother to be Saudi but you did NOT enter her Saudi"
                                     " Government ID"),
            'hs_cert_missing': _('You need to upload your high school certificate since you selected International '
                                 'schooling system')
        })
        self.error_messages = BaseContactForm.error_messages

        for field in self.fields:
            if field not in ['saudi_mother', 'high_school_certificate', 'courses_certificate']:
                self.fields[field].widget.attrs['class'] = 'form-control'

            if field not in ['student_notes', 'third_name_ar', 'second_name_en', 'third_name_en',
                             'gender', 'saudi_mother_gov_id', 'high_school_certificate', 'courses_certificate']:
                self.fields[field].required = True

            if field in ['username2', 'email2', 'mobile2']:
                self.fields[field].widget.attrs.update({'class': 'nocopy form-control'})

        try:
            # this try..except is added for when in Phase1UserEditForm those fields wont exist
            self.fields['nationality'].widget.attrs['class'] = 'select2 form-control'

            self.fields['saudi_mother_gov_id'].validators = [
                RegexValidator(
                    '^\d{9,11}$',
                    message=self.error_messages['govid_invalid']
                )]

            self.fields['password2'].help_text = _('Enter the same password as before, for verification')
            self.fields['high_school_graduation_year'].queryset = GraduationYear.objects.filter(show=True)
        except:
            pass

        if not settings.DISABLE_CAPTCHA:
            # self.fields['captcha'] = ReCaptchaField(label=_('Captcha'), attrs={'lang': translation.get_language()})
            self.fields['captcha'] = CaptchaField(label=_('Confirmation Code'))

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        username1 = cleaned_data.get("username")
        if username1:
            is_saudi = cleaned_data.get('nationality') == 'SA'

            if is_saudi:
                match = re.match(r'^\d{9,11}$', str(username1))
            else:
                match = re.match(r'^\d{7,13}$', str(username1))

            if not match:
                raise forms.ValidationError(
                    self.error_messages['govid_invalid'],
                    code='govid_invalid',
                    )
        high_school_system = cleaned_data.get("high_school_system")
        if (high_school_system == AdmissionRequest.HighSchoolSystems.INTERNATIONAL
                and not cleaned_data.get("high_school_certificate")):
            raise forms.ValidationError(
                self.error_messages['hs_cert_missing'],
                code='high_school_certificate_missing',
            )
        return cleaned_data

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get('password2')
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except forms.ValidationError as error:
                self.add_error('password2', error)

    def clean_username(self):
        username1 = parse_non_standard_numerals(self.cleaned_data.get("username"))
        # username1 = parse_non_standard_numerals(cleaned_data.get("username"))
        denial = DeniedStudent.check_if_student_is_denied(username1)

        if denial:
            raise forms.ValidationError(
                self.error_messages['govid_denied'] + denial,
                code='govid_denied',
                )

        return username1

    def clean_username2(self):
        username1 = parse_non_standard_numerals(self.cleaned_data.get("username"))
        username2 = parse_non_standard_numerals(self.cleaned_data.get("username2"))
        if username1 and username2 and username1 != username2:
            raise forms.ValidationError(
                self.error_messages['govid_mismatch'],
                code='govid_mismatch',
            )
        return username2

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


class Phase1UserEditForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        fields = ['student_full_name_ar', 'student_full_name_en',
                  # 'first_name_ar', 'second_name_ar', 'third_name_ar', 'family_name_ar',
                  # 'first_name_en', 'second_name_en', 'third_name_en', 'family_name_en',
                  'mobile', 'mobile2', 'email', 'email2', 'high_school_system',
                  'high_school_gpa_student_entry', 'student_notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # those fields are in the RegistrationForm but not needed here
        del(self.fields['username'])
        del(self.fields['username2'])
        del(self.fields['password1'])
        del(self.fields['password2'])
        del(self.fields['gender'])
