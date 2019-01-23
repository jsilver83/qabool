from django import forms
from django.utils.translation import ugettext_lazy as _

from ..models import *


class TarifiTimeSlotForm(forms.ModelForm):
    class Meta:
        model = AdmissionRequest
        fields = ['tarifi_week_attendance_date']

    def __init__(self, *args, **kwargs):
        super(TarifiTimeSlotForm, self).__init__(*args, **kwargs)
        self.fields['tarifi_week_attendance_date'].required = True
        self.fields['tarifi_week_attendance_date'].widget = \
            forms.RadioSelect(choices=TarifiReceptionDate.get_all_available_slots(self.instance, False))
