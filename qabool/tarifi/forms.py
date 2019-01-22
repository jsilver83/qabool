from django import forms

from django.utils.translation import ugettext_lazy as _


class TarifiSearchForm(forms.Form):
    kfupm_id = forms.IntegerField(required=True, label=_('KFUPM ID'))
