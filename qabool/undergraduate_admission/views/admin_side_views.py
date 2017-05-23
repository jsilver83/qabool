from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from undergraduate_admission.filters import UserListFilter
from undergraduate_admission.forms.admin_side_forms import CutOffForm, VerifyCommitteeForm, ApplyStatusForm
from undergraduate_admission.models import User
from undergraduate_admission.utils import try_parse_float
from django.utils.translation import ugettext_lazy as _


# def cut_off_point(request):
#     form = CutOffForm(request.GET or None)
#     selected_student_types = request.GET.getlist('student_type', ['S', 'M', 'N'])
#     print(selected_student_types)
#     cut_off_total = try_parse_float(request.GET.get('admission_total', 0.0))
#     print(cut_off_total)
#
#     filtered = UserListFilter(request.GET, queryset=User.objects.all())
#     filtered_with_properties = [student for student in filtered.qs
#                                 if student.student_type in selected_student_types]
#     filtered_with_properties2 = [student for student in filtered_with_properties
#                                  if student.admission_total >= cut_off_total]
#
#     return render(request,
#                   template_name='undergraduate_admission/admin/cutoff.html',
#                   context={'form': form, 'students': filtered_with_properties2})


class AdminBaseView(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser


class CutOffPointView(AdminBaseView, View):
    def get_students_matching(self, request):
        selected_student_types = request.GET.getlist('student_type', ['S', 'M', 'N'])
        # print(selected_student_types)
        cut_off_total = try_parse_float(request.GET.get('admission_total', 0.0))
        # print(cut_off_total)

        filtered = UserListFilter(request.GET, queryset=User.objects.all())
        filtered_with_properties = [student for student in filtered.qs
                                    if student.student_type in selected_student_types]
        filtered_with_properties2 = [student for student in filtered_with_properties
                                     if student.admission_total >= cut_off_total]

        return filtered_with_properties2

    def get(self, request, *args, **kwargs):
        form = CutOffForm(request.GET or None)

        filtered = self.get_students_matching(request)

        form2 = ApplyStatusForm()

        return render(request,
                      template_name='undergraduate_admission/admin/cutoff.html',
                      context={'form': form,
                               'students': filtered,
                               'form2': form2})

    def post(self, request, *args, **kwargs):
        form = CutOffForm(request.GET or None)

        filtered = self.get_students_matching(request)

        form2 = ApplyStatusForm(request.POST or None)

        if form2.is_valid():
            print('valid')
            status = form2.cleaned_data.get('status')
            print(status)

        messages.success(request, _('New status has been applied to students chosen...'))
        return redirect(reverse_lazy('cut_off_point'))


class VerifyCommittee(AdminBaseView, SuccessMessageMixin, UpdateView):
    template_name = 'undergraduate_admission/admin/verify_committee.html'
    form_class = VerifyCommitteeForm
    model = User
    success_message = 'List successfully saved!!!!'

    def get_success_url(self, **kwargs):
        return reverse_lazy('verify_committee', kwargs={'pk': self.kwargs['pk']})
        # def form_valid(self, form):
