from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils.translation import ugettext_lazy as _

from undergraduate_admission.forms.phase2_forms import Phase2Step1Form
from undergraduate_admission.models import AdmissionSemester


def phase2_step1(request):
    form = Phase2Step1Form(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            # request.session['agreed'] = True
            return redirect('register')
        else:
            messages.error(request, _('Error resetting password. Make sure you enter the correct info.'))

    sem = AdmissionSemester.get_phase2_active_semester()
    return render(request, 'undergraduate_admission/register.html', {'form': form,})
