import floppyforms.__future__ as forms
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _

from .models import HousingUser
from undergraduate_admission.models import Lookup, User


class HousingInfoUpdateForm(forms.ModelForm):
    agree1 = forms.BooleanField(label=_('housing terms and conditions 1'))
    agree2 = forms.BooleanField(label=_('housing terms and conditions 2'))
    agree3 = forms.BooleanField(label=_('housing terms and conditions 3'))

    class Meta:
        model = HousingUser
        fields = ['searchable', 'facebook', 'twitter', 'sleeping', 'light', 'room_temperature', 'visits',
                  'interests_and_hobbies', 'agree1', 'agree2', 'agree3']

        SEARCHABLE_CHOICES = (
            ('', "---"),
            (True, _("Looking for roommate")),
            (False, _("Not looking for roommate")),
        )

        widgets = {
            'searchable': forms.Select(choices=SEARCHABLE_CHOICES),
            'sleeping': forms.Select(choices=Lookup.get_lookup_choices('HOUSING_PREF_SLEEPIN')),
            'light': forms.Select(choices=Lookup.get_lookup_choices('HOUSING_PREF_LIGHT')),
            'room_temperature': forms.Select(choices=Lookup.get_lookup_choices('HOUSING_PREF_AC')),
            'visits': forms.Select(choices=Lookup.get_lookup_choices('HOUSING_PREF_VISITS')),
        }

    def clean_agree1(self):
        agree = self.cleaned_data.get("agree1")

        if not agree:
            raise forms.ValidationError(
                message=_('You have to check this box')
            )

    def clean_agree2(self):
        agree = self.cleaned_data.get("agree2")

        if not agree:
            raise forms.ValidationError(
                message=_('You have to check this box')
            )

    def clean_agree3(self):
        agree = self.cleaned_data.get("agree3")

        if not agree:
            raise forms.ValidationError(
                message=_('You have to check this box')
            )

    def clean(self):
        cleaned_data = super(HousingInfoUpdateForm, self).clean()
        searchable = cleaned_data.get('searchable')

        if searchable:
            # facebook = cleaned_data.get('facebook')
            # twitter = cleaned_data.get('twitter')
            sleeping = cleaned_data.get('sleeping')
            light = cleaned_data.get('light')
            room_temperature = cleaned_data.get('room_temperature')
            visits = cleaned_data.get('visits')

            if not (sleeping and light and room_temperature and visits):
                raise forms.ValidationError(_('Enter required values'))


class HousingSearchForm(forms.Form):
    high_school_city = forms.CharField(
        # queryset = User.objects.order_by().values_list('high_school_city').distinct(),
        widget=forms.Select(choices=User.get_distinct_high_school_city()),
        required=False,
        label=_('High School City'),
    )
    high_school_name = forms.CharField(required=False, label=_('High School Name'))
    light = forms.CharField(required=False,
                            label=_('Light'),
                            widget=forms.Select(choices=Lookup.get_lookup_choices('HOUSING_PREF_LIGHT')),
                            )
    room_temperature = forms.CharField(required=False,
                                       label=_('Room Temperature'),
                                       widget=forms.Select(choices=Lookup.get_lookup_choices('HOUSING_PREF_AC')),
                                       )
    visits = forms.CharField(required=False,
                             label=_('Visits'),
                             widget=forms.Select(choices=Lookup.get_lookup_choices('HOUSING_PREF_VISITS')),
                             )
    sleeping = forms.CharField(required=False,
                               label=_('Sleeping'),
                               widget=forms.Select(choices=Lookup.get_lookup_choices('HOUSING_PREF_SLEEPIN')),
                               )


class RoommateRequestForm(forms.Form):
    gov_id_or_kfupm_id = forms.CharField(max_length=12, label=_('KFUPM/Government ID'), validators=[
        RegexValidator(
            '^\d{9,11}$',
            message=_('Invalid KFUPM ID or government ID')
        )])