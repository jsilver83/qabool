import floppyforms.__future__ as forms

from undergraduate_admission.models import User
from django.utils.translation import ugettext_lazy as _, get_language


class Phase2Step1Form(forms.ModelForm):

    # username = forms.CharField(
    #     label=_('Government ID'),
    #     max_length=11,
    #     min_length=9,
    #     help_text=_('National ID for Saudis, Iqama Number for non-Saudis.'),
    #     validators=[
    #         RegexValidator(
    #             '^\d{9,11}$',
    #             message=UserCreationForm.error_messages['govid_invalid']
    #         ),
    #     ]
    # )


    class Meta:
        model = User

        # fields = ['first_name', 'last_name', 'username', 'username2', 'mobile', 'mobile2',
        #           'email', 'email2', 'guardian_mobile', 'high_school_graduation_year', 'nationality',
        #           'saudi_mother', 'password1', 'password2', 'student_notes']
        exclude = ['password', 'date_joined', 'is_staff']

    #     widgets = {
    #         # workaround since __init__ setting to required doesnt work
    #         'email': forms.TextInput(attrs = {'required': ''}),
    #         'first_name': forms.TextInput(attrs = {'required': ''}),
    #         'last_name': forms.TextInput(attrs = {'required': ''}),
    #         'high_school_graduation_year': forms.Select(attrs = {'required': ''}),
    #         'nationality': forms.Select(attrs = {
    #             'required': '',
    #             'class': 'select2',}),
    #         'mobile': forms.TextInput(attrs = {'required': '',
    #                                            'placeholder': '9665xxxxxxxx',
    #                                            }),
    #         'guardian_mobile': forms.TextInput(attrs = {'required': '',
    #                                                    'placeholder': '9665xxxxxxxx',
    #                                                    }),
    #         'saudi_mother': forms.Select(choices = CHOICES),
    #     }
    #     # help_texts = {
    #     #     'username': _('National ID for Saudis, Iqama Number for non-Saudis.'),
    #     # }
    #     # initial = {'username': _('Government ID')}
    #
    def __init__(self, *args, **kwargs):
        super(Phase2Step1Form, self).__init__(*args, **kwargs)
    #     self.fields['first_name'].required = True
    #     self.fields['last_name'].required = True
    #     self.fields['guardian_mobile'].required = True
    #     self.fields['password1'].help_text = _('Minimum length is 8. Use both numbers and characters.')
    #     self.fields['password2'].help_text = _('Enter the same password as before, for verification')
    #     self.fields['password1'].widget = forms.PasswordInput(attrs = {'required':''})
    #     self.fields['password2'].widget = forms.PasswordInput(attrs = {'required':''})
    #     # self.fields['captcha'] = ReCaptchaField(label=_('Captcha'), attrs={'lang': translation.get_language()})
    #
    # def clean_data(self):
    #     super(RegistrationForm, self).clean_data(self)
    #
    # def clean_username(self):
    #     username1 = self.cleaned_data.get("username")
    #     denial = DeniedStudent.check_if_student_is_denied(username1)
    #
    #     if denial:
    #         raise forms.ValidationError(
    #             self.error_messages['govid_denied'] + denial,
    #             code='govid_denied',
    #         )
    #     return username1
    #
    # def clean_username2(self):
    #     username1 = self.cleaned_data.get("username")
    #     username2 = self.cleaned_data.get("username2")
    #     if username1 and username2 and username1 != username2:
    #         raise forms.ValidationError(
    #             self.error_messages['govid_mismatch'],
    #             code='govid_mismatch',
    #         )
    #     return username2
    #
    # def clean_email(self):
    #     email = self.cleaned_data.get("email")
    #     semester = AdmissionSemester.get_phase1_active_semester()
    #     found = User.objects.filter(email=email, semester=semester)
    #     if email and found:
    #         raise forms.ValidationError(
    #             self.error_messages['email_not_unique'],
    #             code='email_not_unique',
    #         )
    #     return email
    #
    # def clean_email2(self):
    #     email1 = self.cleaned_data.get("email")
    #     email2 = self.cleaned_data.get("email2")
    #     if email1 and email2 and email1 != email2:
    #         raise forms.ValidationError(
    #             self.error_messages['email_mismatch'],
    #             code='email_mismatch',
    #         )
    #     return email2
    #
    # def clean_mobile(self):
    #     mobile = self.cleaned_data.get("mobile")
    #     semester = AdmissionSemester.get_phase1_active_semester()
    #     found = User.objects.filter(mobile=mobile, semester=semester)
    #     if mobile and found:
    #         raise forms.ValidationError(
    #             self.error_messages['mobile_not_unique'],
    #             code='mobile_not_unique',
    #         )
    #     return mobile
    #
    # def clean_mobile2(self):
    #     mobile1 = self.cleaned_data.get("mobile")
    #     mobile2 = self.cleaned_data.get("mobile2")
    #     if mobile1 and mobile2 and mobile1 != mobile2:
    #         raise forms.ValidationError(
    #             self.error_messages['mobile_mismatch'],
    #             code='mobile_mismatch',
    #         )
    #     return mobile2
    #
    # def clean_guardian_mobile(self):
    #     mobile1 = self.cleaned_data.get("mobile")
    #     mobile2 = self.cleaned_data.get("guardian_mobile")
    #     if mobile1 and mobile2 and mobile1 == mobile2:
    #         raise forms.ValidationError(
    #             self.error_messages['guardian_mobile_match'],
    #             code='guardian_mobile_match',
    #         )
    #     return mobile2
    #
    #
