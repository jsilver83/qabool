from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect

from shared_app.utils import get_current_admission_request_for_logged_in_user


class StudentMixin(LoginRequiredMixin, UserPassesTestMixin):
    admission_request = None

    def test_func(self):
        return self.admission_request is not None

    def init_class_variables(self, request, *args, **kwargs):
        self.admission_request = get_current_admission_request_for_logged_in_user(request)

    def dispatch(self, request, *args, **kwargs):
        self.init_class_variables(request, *args, **kwargs)

        if request.user.is_authenticated:
            if request.user.is_superuser:
                return redirect('undergraduate_admission:verify_list')
        return super(StudentMixin, self).dispatch(request, *args, **kwargs)
