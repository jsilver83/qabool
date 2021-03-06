from django import template
from django.core.exceptions import ObjectDoesNotExist

# from find_roommate.models import RoommateRequest
from shared_app.utils import get_current_admission_request_for_logged_in_user
from undergraduate_admission.models import AdmissionSemester, RegistrationStatus

register = template.Library()


@register.inclusion_tag('undergraduate_admission/_student_info_commands.html', takes_context=True)
def student_info_commands(context):
    admission_request = get_current_admission_request_for_logged_in_user(context['request'])

    phase = admission_request.get_student_phase()
    status_css_class = 'info'
    if phase in [RegistrationStatus.GeneralStatuses.PARTIALLY_ADMITTED, RegistrationStatus.GeneralStatuses.ADMITTED]:
        status_css_class = 'success'
    elif phase == RegistrationStatus.GeneralStatuses.WITHDRAWN:
        status_css_class = 'default'
    elif phase == RegistrationStatus.GeneralStatuses.REJECTED:
        status_css_class = 'danger'

    return {
        'admission_request': admission_request,
        'status_css_class': status_css_class,
    }
