from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, get_object_or_404
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from undergraduate_admission.filters import UserListFilter
from undergraduate_admission.forms.admin_side_forms import CutOffForm, VerifyCommitteeForm
from undergraduate_admission.models import User
from undergraduate_admission.utils import try_parse_float


def cut_off_point(request):
    form = CutOffForm(request.GET or None)
    selected_student_types = request.GET.getlist('student_type', ['S', 'M', 'N'])
    print(selected_student_types)
    cut_off_total = try_parse_float(request.GET.get('admission_total', 0.0))
    print(cut_off_total)

    filtered = UserListFilter(request.GET, queryset=User.objects.all())
    filtered_with_properties = [student for student in filtered.qs
                                if student.student_type in selected_student_types]
    filtered_with_properties = [student for student in filtered_with_properties
                                if student.admission_total > cut_off_total]

    return render(request,
                  template_name='undergraduate_admission/admin/cutoff.html',
                  context={'form': form, 'students': filtered_with_properties})


class VerifyCommittee(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = 'undergraduate_admission/admin/verify_committee.html'
    form_class = VerifyCommitteeForm
    model = User
    success_message = 'List successfully saved!!!!'

    def get_success_url(self, **kwargs):
        return reverse_lazy('verify_committee', kwargs={'pk': self.kwargs['pk']})
    # def form_valid(self, form):
