from captcha.fields import CaptchaField
from django import forms
from django.contrib.auth import password_validation, get_user_model
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
# from captcha.fields import ReCaptchaField
from django.utils.translation import ugettext_lazy as _

from shared_app.base_forms import BaseCrispyForm
from undergraduate_admission.utils import parse_non_standard_numerals
from ..models import *

User = get_user_model()


class MyPasswordChangeForm(BaseCrispyForm, PasswordChangeForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(MyPasswordChangeForm, self).__init__(*args, **kwargs)


class BaseContactForm(BaseCrispyForm, forms.ModelForm):
    error_messages = {
        'email_mismatch': _("The two email fields didn't match."),
        'mobile_mismatch': _("The two mobile fields didn't match."),
        'email_not_unique': _("The Email entered is associated with another applicant. "
                              "Please use a different Email"),
        'mobile_not_unique': _("The Mobile entered is associated with another applicant. "
                               "Please use a different Mobile"),
    }

    email = forms.EmailField(
        label=_('Email Address'),
        required=True,
        widget=forms.EmailInput()
    )
    email2 = forms.EmailField(
        label=_('Email Address Confirmation'),
        required=True,
        help_text=_('Enter the same email address as before, for verification'),
        widget=forms.EmailInput(attrs={'class': 'nocopy'})
    )
    mobile2 = forms.CharField(
        label=_('Mobile Confirmation'),
        max_length=12,
        required=True,
        help_text=_('Enter the same mobile number as before, for verification'),
        widget=forms.TextInput(attrs={'class': 'nocopy'})
    )

    class Meta:
        model = AdmissionRequest
        fields = ['email', 'email2', 'mobile', 'mobile2']
        widgets = {
            'email': forms.TextInput(attrs={'required': ''}),
            'mobile': forms.TextInput(attrs={'required': '',
                                             'placeholder': '9665xxxxxxxx', }),
        }

    def __init__(self, *args, **kwargs):
        self.user = None
        try:
            request = kwargs.pop('request', None)
            self.user = request.user
        except:
            pass

        super(BaseContactForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        if self.user:
            self.initial['email'] = self.user.email

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if self.user:
            found = User.objects.filter(email=email).exclude(id=self.user.pk)
        else:
            found = User.objects.filter(email=email)
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
        if self.instance.pk:
            found = AdmissionRequest.objects.filter(mobile=mobile, semester=semester).exclude(id=self.instance.pk)
        else:
            found = AdmissionRequest.objects.filter(mobile=mobile, semester=semester)
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

    def save(self, commit=True):
        saved = super(BaseContactForm, self).save(commit=False)
        saved.user.email = self.cleaned_data['email']

        if commit:
            saved.user.save()
            saved.save()

        return saved


class MyAuthenticationForm(BaseCrispyForm, AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(MyAuthenticationForm, self).__init__(self, *args, **kwargs)
        self.fields['username'].label = _('Government ID')

        self.fields['username'].widget = forms.TextInput(attrs={'required': '',
                                                                'placeholder': _('Government ID')
                                                                })
        self.fields['password'].widget = forms.PasswordInput(attrs={'required': '',
                                                                    'placeholder': _('password')
                                                                    })

        if not settings.DISABLE_CAPTCHA:
            # self.fields['captcha'] = ReCaptchaField(label=_('Captcha'), attrs={'lang': translation.get_language()})
            self.fields['captcha'] = CaptchaField(label=_('Confirmation Code'))

    def clean_username(self):
        return parse_non_standard_numerals(self.cleaned_data.get("username"))


class ForgotPasswordForm(BaseCrispyForm, forms.ModelForm):
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
        'wrong_entry': _('Error resetting password. Make sure you enter the correct info.'),
    }

    govid = forms.CharField(
        label=_('Government ID'),
        max_length=50,
        required=True,
        help_text=_('National ID for Saudis, Iqama Number for non-Saudis.'),
    )

    # id2 = forms.IntegerField(
    #     label=_('Registration Number'),
    #     required=False,
    # )

    email = forms.EmailField(label=_("Email"), max_length=254)

    password1 = forms.CharField(
        label=_('New Password'),
        max_length=50,
        required=True,
        help_text=_('Minimum length is 8. Use both numbers and characters.'),
        widget=forms.PasswordInput(),
    )

    password2 = forms.CharField(
        label=_('New Password confirmation'),
        max_length=50,
        required=True,
        help_text=_('Enter the same password as before, for verification'),
        widget=forms.PasswordInput(),
    )

    class Meta:
        model = AdmissionRequest
        fields = ['govid', 'mobile', 'guardian_mobile', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(ForgotPasswordForm, self).__init__(*args, **kwargs)

        self.fields['guardian_mobile'].required = True

        if not settings.DISABLE_CAPTCHA:
            # self.fields['captcha'] = ReCaptchaField(label=_('Captcha'), attrs={'lang': translation.get_language()})
            self.fields['captcha'] = CaptchaField(label=_('Confirmation Code'))

    def clean_govid(self):
        return parse_non_standard_numerals(self.cleaned_data.get("govid"))

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )

        matching_users = User.objects.filter(username=cleaned_data.get('govid'),
                                             email=cleaned_data.get('email'))
        if matching_users and matching_users.count() == 1:
            user = matching_users.first()
            admission_request = AdmissionRequest.objects.filter(user=user,
                                                                mobile=cleaned_data.get("mobile"),
                                                                guardian_mobile=cleaned_data.get("guardian_mobile"))

            if admission_request:
                self.instance = admission_request.first()
                password_validation.validate_password(cleaned_data.get('password2'), user)

        if self.instance.pk is None:
            raise forms.ValidationError(
                    self.error_messages['wrong_entry'],
                    code='wrong_entry',
                )

        return cleaned_data

    def save(self, commit=True):
        if self.instance.pk:
            password = self.cleaned_data.get("password1")
            self.instance.user.set_password(password)
            self.instance.user.save()
            return self.instance
        else:
            return None
