import floppyforms.__future__ as forms
from django.utils import timezone

from undergraduate_admission.models import User, Lookup, RegistrationStatusMessage
from django.utils.translation import ugettext_lazy as _, get_language

YES_NO_CHOICES = (
    ('True', _("Yes")),
    ('False', _("No")),
)


class TarifiTimeSlotForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['id', ]

    def save(self, commit=True):
        instance = super(TarifiTimeSlotForm, self).save(commit=False)
        instance.phase2_submit_date = timezone.now()
        if commit:
            instance.save()
            return instance
        else:
            return instance