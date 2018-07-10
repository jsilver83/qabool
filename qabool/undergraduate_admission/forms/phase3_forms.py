import floppyforms.__future__ as forms
from django.utils.translation import ugettext_lazy as _

from undergraduate_admission.models import User, RegistrationStatusMessage, TarifiReceptionDate


class TarifiTimeSlotForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['tarifi_week_attendance_date']

    def __init__(self, *args, **kwargs):
        super(TarifiTimeSlotForm, self).__init__(*args, **kwargs)
        self.fields['tarifi_week_attendance_date'].required = True
        self.fields['tarifi_week_attendance_date'].widget = \
            forms.RadioSelect(choices=TarifiReceptionDate.get_all_available_slots(self.instance, False))


class ChooseRoommateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['roommate_id']

    def clean_roommate_id(self):
        roommate_id = self.cleaned_data.get("roommate_id")
        if not User.objects.filter(username=roommate_id,
                                   eligible_for_housing=True,
                                   status_message=RegistrationStatusMessage.get_status_admitted_final()):
            raise forms.ValidationError(
                _('This ID does not exist.'),
                code='roommate_does_not_exist',
            )
        return roommate_id
