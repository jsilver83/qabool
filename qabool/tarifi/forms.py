from django import forms

from django.utils.translation import ugettext_lazy as _

from shared_app.base_forms import BaseCrispyForm


class TarifiSearchForm(BaseCrispyForm, forms.Form):
    kfupm_id_gov_id = forms.IntegerField(required=True, label=_('KFUPM ID or Government ID'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['kfupm_id_gov_id'].widget.attrs.update({'class': 'form-control'})


class ReceptionDeskForm(BaseCrispyForm, forms.Form):
    reception_desk = forms.IntegerField(required=True, label=_('Reception Desk'))


class CourseAttendanceSearchForm(BaseCrispyForm, forms.Form):
    kfupm_id = forms.IntegerField(required=True, label=_('KFUPM ID'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['kfupm_id'].widget.attrs.update({'class': 'form-control'})
