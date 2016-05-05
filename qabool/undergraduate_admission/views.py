from django.shortcuts import render, redirect
from django.views.generic import DetailView
from django.views.generic.edit import CreateView
from django.http import HttpResponse
from django.core.urlresolvers import reverse_lazy
from datetime import date

from .models import User
from .forms import RegistrationForm

# Create your views here.

# class IndexView(DetailView):
#     template_name = 'undergraduate_admission/index.html'
#
#     def get_context_data(self, pk, **kwargs):
#         user = Student.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')

def IndexView(request):
    user = User.objects.create_user('john6', 'lennon@thebeatles.com', 'johnpassword')

    return HttpResponse(status=201)

class RegisterView(CreateView):
    model = User
    context_object_name = "user"
    form_class = RegistrationForm
    template_name = 'undergraduate_admission/register.html'
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        usr = User.objects.create_user(form.instance.username, form.instance.email, form.instance.password, admission_note='Test note')
        print (form.cleaned_data)
        return redirect(self.success_url)
