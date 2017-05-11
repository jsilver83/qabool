from captcha.fields import CaptchaField
# from captcha.fields import ReCaptchaField
from django.utils import translation
from django.utils.translation import ugettext_lazy as _, get_language
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm

from qabool import settings
from undergraduate_admission.models import User, AdmissionSemester
import floppyforms.__future__ as forms

from undergraduate_admission.utils import try_parse_int


class MyPasswordChangeForm(PasswordChangeForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(MyPasswordChangeForm, self).__init__(*args, **kwargs)


class BaseContactForm(forms.ModelForm):
    error_messages = {
        'email_mismatch': _("The two email fields didn't match."),
        'mobile_mismatch': _("The two mobile fields didn't match."),
        'email_not_unique': _("The Email entered is associated with another applicant. "
                              "Please use a different Email"),
        'mobile_not_unique': _("The Mobile entered is associated with another applicant. "
                               "Please use a different Mobile"),
    }

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
        model = User
        fields = ['email', 'email2', 'mobile', 'mobile2']
        widgets = {
            'email': forms.TextInput(attrs={'required': ''}),
            'mobile': forms.TextInput(attrs={'required': '',
                                             'placeholder': '9665xxxxxxxx',
                                             }),
        }

    def __init__(self, *args, **kwargs):
        self.user_id = -1
        try:
            request = kwargs.pop('request', None)
            self.user_id = request.user.id
        except:
            pass

        print(self.user_id)

        super(BaseContactForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True

    def clean_email(self):
        email = self.cleaned_data.get("email")
        semester = AdmissionSemester.get_phase1_active_semester()
        found = User.objects.filter(email=email, semester=semester).exclude(id=self.user_id)
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
        mobile = try_parse_int(self.cleaned_data.get("mobile"))
        semester = AdmissionSemester.get_phase1_active_semester()
        found = User.objects.filter(mobile=mobile, semester=semester).exclude(id=self.user_id)
        if mobile and found:
            raise forms.ValidationError(
                self.error_messages['mobile_not_unique'],
                code='mobile_not_unique',
            )
        return mobile

    def clean_mobile2(self):
        mobile1 = try_parse_int(self.cleaned_data.get("mobile"))
        mobile2 = try_parse_int(self.cleaned_data.get("mobile2"))
        if mobile1 and mobile2 and mobile1 != mobile2:
            raise forms.ValidationError(
                self.error_messages['mobile_mismatch'],
                code='mobile_mismatch',
            )
        return mobile2


class MyAuthenticationForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(MyAuthenticationForm, self).__init__(self, *args, **kwargs)
        self.fields['username'].label = _('Government ID')
        self.fields['username'].widget = forms.TextInput(attrs={'required': ''})
        self.fields['password'].widget = forms.PasswordInput(attrs={'required': ''})

        if not settings.DISABLE_CAPTCHA:
            # self.fields['captcha'] = ReCaptchaField(label=_('Captcha'), attrs={'lang': translation.get_language()})
            self.fields['captcha'] = CaptchaField(label=_('Confirmation Code'))

    def clean_username(self):
        return try_parse_int(self.cleaned_data.get("username"))


class ForgotPasswordForm(forms.ModelForm):
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }

    govid = forms.CharField(
        label=_('Government ID'),
        max_length=50,
        required=True,
    )

    id2 = forms.IntegerField(
        label=_('Registration Number'),
        required=True,
    )

    password1 = forms.CharField(
        label=_('Password'),
        max_length=50,
        required=True,
        help_text= _('Minimum length is 8. Use both numbers and characters.'),
        widget = forms.PasswordInput(),
    )

    password2 = forms.CharField(
        label=_('Password confirmation'),
        max_length=50,
        required=True,
        help_text= _('Enter the same password as before, for verification'),
        widget = forms.PasswordInput(),
    )

    class Meta:
        model = User
        fields = ['govid', 'id2', 'email', 'mobile', 'password1', 'password2']

        help_texts = {
            'govid': _('National ID for Saudis, Iqama Number for non-Saudis.'),
        }

    def __init__(self, *args, **kwargs):
        super(ForgotPasswordForm, self).__init__(*args, **kwargs)

        if not settings.DISABLE_CAPTCHA:
            # self.fields['captcha'] = ReCaptchaField(label=_('Captcha'), attrs={'lang': translation.get_language()})
            self.fields['captcha'] = CaptchaField(label=_('Confirmation Code'))

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        self.instance.username = self.cleaned_data.get('username')
        password_validation.validate_password(self.cleaned_data.get('password2'), self.instance)
        return password2

    def clean_username(self):
        return try_parse_int(self.cleaned_data.get("username"))

    def save(self):
        username = self.cleaned_data.get("govid")
        password = self.cleaned_data.get("password1")
        email = self.cleaned_data.get("email")
        mobile = self.cleaned_data.get("mobile")
        id2 = self.cleaned_data.get("id2")

        # match 2 out of three values supplied by user
        try:
            user = User.objects.get(username=username, email=email, mobile=mobile)
        except User.DoesNotExist:
            try:
                user = User.objects.get(username=username, email=email, id=id2)
            except User.DoesNotExist:
                try:
                    user = User.objects.get(username=username, mobile=mobile, id=id2)
                except User.DoesNotExist:
                    user = None

        if user is not None:
            user.set_password(password)
            user.save()
            return user
        else:
            return None
