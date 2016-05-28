from captcha.fields import CaptchaField
# from captcha.fields import ReCaptchaFieldfrom django.utils import translation

from django.utils.translation import ugettext_lazy as _, get_language
import floppyforms.__future__ as forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator

from qabool import settings
from undergraduate_admission.models import AdmissionSemester, DeniedStudent, User, Lookup


class AgreementForm(forms.Form):
    agree1 = forms.BooleanField(label=_('I have read all of the above terms and conditions for applying to KFUPM'))
    agree2 = forms.BooleanField(label=_('I accept all the above terms and conditions'))

    def clean_agree1(self):
        agree1 = self.cleaned_data.get("agree1")

        if not agree1:
            raise forms.ValidationError(
                message=_('You have to check this box')
            )

    def clean_agree2(self):
        agree2 = self.cleaned_data.get("agree2")

        if not agree2:
            raise forms.ValidationError(
                message=_('You have to check this box')
            )


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
            'guardian_mobile_match': _("You have entered the guardian mobile same as your own mobile")
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
        max_length=11,
        min_length=9,
        help_text=_('National ID for Saudis, Iqama Number for non-Saudis. e.g. 1xxxxxxxxx or 2xxxxxxxxx'),
        validators=[
            RegexValidator(
                '^\d{9,11}$',
                message=UserCreationForm.error_messages['govid_invalid']
            ),
        ]
    )
    username2 = forms.CharField(
        label=_('Government ID Confirmation'),
        max_length=11,
        min_length=9,
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

    # high_school_system = forms.ModelChoiceField(
    #     queryset=Lookup.objects.filter(show=True, lookup_type='HIGH_SCHOOL_TYPE'),
    #     required=True,
    # )

    class Meta:
        model = User

        fields = ['first_name', 'last_name', 'username', 'username2', 'mobile', 'mobile2',
                  'email', 'email2', 'guardian_mobile', 'high_school_graduation_year', 'high_school_system',
                  'nationality', 'saudi_mother', 'password1', 'password2', 'student_notes']

        SAUDI_MOTHER_CHOICES = (
            ('', "---"),
            (True, _("Yes")),
            (False, _("No")),
        )

        widgets = {
            # workaround since __init__ setting to required doesnt work
            'email': forms.TextInput(attrs={'required': ''}),
            'first_name': forms.TextInput(attrs={'required': ''}),
            'last_name': forms.TextInput(attrs={'required': ''}),
            'high_school_graduation_year': forms.Select(attrs={'required': ''}),
            'nationality': forms.Select(attrs={
                'required': '',
                'class': 'select2',}),
            'mobile': forms.TextInput(attrs={'required': '',
                                             'placeholder': '9665xxxxxxxx',
                                             }),
            'guardian_mobile': forms.TextInput(attrs={'required': '',
                                                      'placeholder': '9665xxxxxxxx',
                                                      }),
            'saudi_mother': forms.Select(choices=SAUDI_MOTHER_CHOICES),
        }
        # help_texts = {
        #     'username': _('National ID for Saudis, Iqama Number for non-Saudis.'),
        # }
        # initial = {'username': _('Government ID')}

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['guardian_mobile'].required = True
        self.fields['password1'].help_text = _('Minimum length is 8. Use both numbers and characters.')
        self.fields['password2'].help_text = _('Enter the same password as before, for verification')
        self.fields['password1'].widget = forms.PasswordInput(attrs={'required': ''})
        self.fields['password2'].widget = forms.PasswordInput(attrs={'required': ''})
        self.fields['high_school_system'].widget = forms.Select(choices= Lookup.get_lookup_choices('HIGH_SCHOOL_TYPE'))
        self.fields['high_school_system'].required = True

        if not settings.DISABLE_CAPTCHA:
            # self.fields['captcha'] = ReCaptchaField(label=_('Captcha'), attrs={'lang': translation.get_language()})
            self.fields['captcha'] = CaptchaField(label=_('Captcha'))

    def clean_data(self):
        super(RegistrationForm, self).clean_data(self)

    def clean_username(self):
        username1 = self.cleaned_data.get("username")
        denial = DeniedStudent.check_if_student_is_denied(username1)

        if denial:
            raise forms.ValidationError(
                self.error_messages['govid_denied'] + denial,
                code='govid_denied',
            )
        return username1

    def clean_username2(self):
        username1 = self.cleaned_data.get("username")
        username2 = self.cleaned_data.get("username2")
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
        mobile = self.cleaned_data.get("mobile")
        semester = AdmissionSemester.get_phase1_active_semester()
        found = User.objects.filter(mobile=mobile, semester=semester)
        if mobile and found:
            raise forms.ValidationError(
                self.error_messages['mobile_not_unique'],
                code='mobile_not_unique',
            )
        return mobile

    def clean_mobile2(self):
        mobile1 = self.cleaned_data.get("mobile")
        mobile2 = self.cleaned_data.get("mobile2")
        if mobile1 and mobile2 and mobile1 != mobile2:
            raise forms.ValidationError(
                self.error_messages['mobile_mismatch'],
                code='mobile_mismatch',
            )
        return mobile2

    def clean_guardian_mobile(self):
        mobile1 = self.cleaned_data.get("mobile")
        mobile2 = self.cleaned_data.get("guardian_mobile")
        if mobile1 and mobile2 and mobile1 == mobile2:
            raise forms.ValidationError(
                self.error_messages['guardian_mobile_match'],
                code='guardian_mobile_match',
            )
        return mobile2
