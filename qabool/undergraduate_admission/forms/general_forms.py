from django.utils.translation import ugettext_lazy as _, get_language
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm

from undergraduate_admission.models import User
import floppyforms.__future__ as forms


class MyAuthenticationForm(AuthenticationForm):
    # captcha = ReCaptchaField()

    def __init__(self, *args, **kwargs):
        # lang = kwargs.pop('lang')
        super(MyAuthenticationForm, self).__init__(self, *args, **kwargs)
        self.fields['username'].label = _('Government ID')
        self.fields['username'].widget = forms.TextInput(attrs={'required': ''})
        self.fields['password'].widget = forms.PasswordInput(attrs={'required': ''})
        # self.fields['captcha'] = ReCaptchaField(label=_('Captcha'), attrs={'lang': translation.get_language()})


class ForgotPasswordForm(forms.ModelForm):
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }

    # captcha = ReCaptchaField()

    govid = forms.CharField(
        label=_('Government ID'),
        max_length=50,
        required=True,
        # help_text= _('Enter the same mobile number as before, for verification'),
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
        # self.fields['captcha'] = ReCaptchaField(label=_('Captcha'), attrs={'lang': translation.get_language()})

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

    def save(self):
        username = self.cleaned_data.get("govid")
        password = self.cleaned_data.get("password1")
        email = self.cleaned_data.get("email")
        mobile = self.cleaned_data.get("mobile")
        id = self.cleaned_data.get("id2")

        # match 2 out of three values supplied by user
        try:
            user = User.objects.get(username=username, email=email, mobile=mobile)
        except User.DoesNotExist:
            try:
                user = User.objects.get(username=username, email=email, id=id)
            except User.DoesNotExist:
                try:
                    user = User.objects.get(username=username, mobile=mobile, id=id)
                except User.DoesNotExist:
                    user = None

        if user is not None:
            user.set_password(self.cleaned_data["password1"])
            user.save()
            return user
        else:
            return None
