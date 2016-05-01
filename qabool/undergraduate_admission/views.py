from django.shortcuts import render

from .models import Student
from django.views.generic import DetailView
from django.http import HttpResponse

# Create your views here.

# class IndexView(DetailView):
#     template_name = 'undergraduate_admission/index.html'
#
#     def get_context_data(self, pk, **kwargs):
#         user = Student.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')

def IndexView(request):
    user = Student.objects.create_user('john3', 'lennon@thebeatles.com', 'johnpassword')

    return HttpResponse(status=201)
