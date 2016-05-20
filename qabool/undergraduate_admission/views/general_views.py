from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from django.utils.translation import ugettext_lazy as _

from undergraduate_admission.forms.general_forms import MyAuthenticationForm, ForgotPasswordForm


def index(request, template_name='undergraduate_admission/login.html'):
    if request.method == 'GET' and request.user.is_authenticated():
        return redirect(reverse('student_area'))

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)

                if user.is_superuser:
                    return redirect('/admin')
                else:
                    return redirect(reverse('student_area'))

        else:
            form = MyAuthenticationForm(request.POST)
    else:
        form = MyAuthenticationForm()

    return render(request, template_name, {'form': form})



def forgot_password(request):
    form = ForgotPasswordForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            saved = form.save()
            if saved:
                messages.success(request, _('Password was reset successfully...'))
                return redirect(reverse('index'))
            else:
                messages.error(request, _('Error resetting password. Make sure you enter the correct info.'))

    return render(request, 'undergraduate_admission/forgot_password.html', {'form': form})

@login_required
def student_area(request):
    return render(request, 'undergraduate_admission/student_area.html', context={'user': request.user})
