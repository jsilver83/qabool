import floppyforms.__future__ as forms
from django.utils import timezone

from undergraduate_admission.models import User, Lookup, RegistrationStatusMessage, TarifiReceptionDate
from django.utils.translation import ugettext_lazy as _, get_language


class TarifiTimeSlotForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['tarifi_week_attendance_date']


class ChooseRoommateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['roommate_id']

    def clean_roommate_id(self):
        roommate_id = self.cleaned_data.get("roommate_id")
        if not User.objects.filter(username=roommate_id,
                               eligible_for_housing=True,
                               status_message=RegistrationStatusMessage.get_status_admitted()):
            raise forms.ValidationError(
                _('This ID does not exist.'),
                code='roommate_does_not_exist',
            )
        return roommate_id