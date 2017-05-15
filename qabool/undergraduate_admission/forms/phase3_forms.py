import floppyforms.__future__ as forms
from django.utils import timezone

from undergraduate_admission.models import User, Lookup, RegistrationStatusMessage, TarifiReceptionDate
from django.utils.translation import ugettext_lazy as _, get_language


class TarifiTimeSlotForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['tarifi_week_attendance_date', ]

    def __init__(self, *args, **kwargs):
        super(TarifiTimeSlotForm, self).__init__()
        self.user = kwargs.pop('user')
        self.fields['tarifi_week_attendance_date'].widget = forms.Select(choices=TarifiReceptionDate.
                                                    get_all_available_slots(self.user, add_dashes=True))