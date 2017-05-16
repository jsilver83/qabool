from django import template
from django.core.exceptions import ObjectDoesNotExist

from undergraduate_admission.models import AdmissionSemester

register = template.Library()


@register.inclusion_tag('undergraduate_admission/_student_info_commands.html', takes_context=True)
def admin_commands(context):
    user = context['request'].user
    phase = user.get_student_phase()
    can_withdraw = phase == 'ADMITTED' and not user.tarifi_week_attendance_date
    can_print_withdrawal_letter = phase == 'WITHDRAWN'
    can_print_docs = phase == 'ADMITTED'
    can_confirm = phase == 'PARTIALLY-ADMITTED'
    can_see_kfupm_id = (phase == 'ADMITTED' and user.kfupm_id)
    can_see_housing = (phase == 'ADMITTED' and user.eligible_for_housing)
    try:
        can_search_in_housing = can_see_housing and user.housing_user.searchable
    except ObjectDoesNotExist:
        can_search_in_housing = False
    has_pic = phase == 'PARTIALLY-ADMITTED' or phase == 'ADMITTED'
    can_edit_phase1_info = phase == 'APPLIED' and AdmissionSemester.check_if_phase1_is_active()
    can_edit_contact_info = phase != 'REJECTED'\
                            and phase != 'WITHDRAWN' \
                            and phase != 'ADMITTED' \
                            and not can_edit_phase1_info

    status_css_class = 'info'
    if phase == 'PARTIALLY-ADMITTED' or phase == 'ADMITTED':
        status_css_class = 'success'
    elif phase == 'WITHDRAWN':
        status_css_class = 'default'
    elif phase == 'REJECTED':
        status_css_class = 'danger'
    # else:
    #     status_css_class = 'info'

    return {
        'user': user,
        'can_withdraw': can_withdraw,
        'can_print_docs': can_print_docs,
        'can_confirm': can_confirm,
        'has_pic': has_pic,
        'can_edit_phase1_info': can_edit_phase1_info,
        'can_edit_contact_info': can_edit_contact_info,
        'status_css_class': status_css_class,
        'can_print_withdrawal_letter': can_print_withdrawal_letter,
        'can_see_kfupm_id': can_see_kfupm_id,
        'can_see_housing': can_see_housing,
        'can_search_in_housing': can_search_in_housing,
    }