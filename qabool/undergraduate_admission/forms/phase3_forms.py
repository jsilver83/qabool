import floppyforms.__future__ as forms
from django.utils import timezone

from undergraduate_admission.models import User, Lookup, RegistrationStatusMessage, TarifiReceptionDate
from django.utils.translation import ugettext_lazy as _, get_language


class TarifiTimeSlotForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['tarifi_week_attendance_date', ]