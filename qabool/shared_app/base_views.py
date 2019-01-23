from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from shared_app.utils import get_current_admission_request_for_logged_in_user


class StudentMixin(LoginRequiredMixin, UserPassesTestMixin):
    admission_request = None

    def test_func(self):
        # TODO: fix
        return True

    def init_class_variables(self, request, *args, **kwargs):
        self.admission_request = get_current_admission_request_for_logged_in_user(request)

    def dispatch(self, request, *args, **kwargs):
        self.init_class_variables(request, *args, **kwargs)
        return super(StudentMixin, self).dispatch(request, *args, **kwargs)
