from django.contrib.auth import password_validation
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _, get_language
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils import translation

from captcha.fields import ReCaptchaField
import floppyforms.__future__ as forms

from .models import User, DeniedStudent, AdmissionSemester


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


class AgreementForm(forms.Form):
    agree1 = forms.BooleanField(label=_('I have read all of the above terms and conditions for applying to KFUPM'))
    agree2 = forms.BooleanField(label=_('I accep all the above terms and conditions'))

    def clean_agree1(self):
        agree1 = self.cleaned_data.get("agree1")

        if not agree1:
            raise forms.ValidationError(
                message = _('You have to check this box')
            )

    def clean_agree2(self):
        agree2 = self.cleaned_data.get("agree2")

        if not agree2:
            raise forms.ValidationError(
                message = _('You have to check this box')
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

    # captcha = ReCaptchaField()

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
        help_text=_('National ID for Saudis, Iqama Number for non-Saudis.'),
        validators=[
            RegexValidator(
                '^\d{9-11}$',
                message=UserCreationForm.error_messages['govid_invalid']
            ),
        ]
    )
    username2 = forms.CharField(
        label=_('Government ID Confirmation'),
        max_length=11,
        min_length=9,
        required=True,
        help_text= _('Enter the same government ID as before, for verification'),
        widget = forms.TextInput(attrs = {'class':'nocopy'})
    )
    mobile2 = forms.CharField(
        label=_('Mobile Confirmation'),
        max_length=12,
        required=True,
        help_text= _('Enter the same mobile number as before, for verification'),
        widget = forms.TextInput(attrs = {'class':'nocopy'})
    )

    class Meta:
        model = User

        fields = ['first_name', 'last_name', 'username', 'username2', 'mobile', 'mobile2',
                  'email', 'email2', 'guardian_mobile', 'high_school_graduation_year', 'nationality',
                  'saudi_mother', 'password1', 'password2']
        CHOICES = (
            ('', "---"),
            (True, _("Yes")),
            (False, _("No")),
        )

        widgets = {
            # workaround since __init__ setting to required doesnt work
            'email': forms.TextInput(attrs = {'required': ''}),
            'first_name': forms.TextInput(attrs = {'required': ''}),
            'last_name': forms.TextInput(attrs = {'required': ''}),
            'high_school_graduation_year': forms.Select(attrs = {'required': ''}),
            'nationality': forms.Select(attrs = {
                'required': '',
                'class': 'select2',}),
            'mobile': forms.TextInput(attrs = {'required': ''}),
            'guardian_mobile': forms.TextInput(attrs = {'required': ''}),
            'saudi_mother': forms.Select(choices = CHOICES),
        }
        # help_texts = {
        #     'username': _('National ID for Saudis, Iqama Number for non-Saudis.'),
        # }
        # initial = {'username': _('Government ID')}

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['guardian_mobile'].required = True
        self.fields['password1'].help_text = _('Minimum length is 8. Use both numbers and characters.')
        self.fields['password2'].help_text = _('Enter the same password as before, for verification')
        self.fields['password1'].widget = forms.PasswordInput(attrs = {'required':''})
        self.fields['password2'].widget = forms.PasswordInput(attrs = {'required':''})
        # self.fields['captcha'] = ReCaptchaField(label=_('Captcha'), attrs={'lang': translation.get_language()})

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