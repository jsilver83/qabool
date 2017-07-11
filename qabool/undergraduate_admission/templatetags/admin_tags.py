from django import template
from django.core.exceptions import ObjectDoesNotExist

from undergraduate_admission.models import AdmissionSemester

register = template.Library()


@register.inclusion_tag('undergraduate_admission/admin/_admin_commands.html', takes_context=True)
def admin_commands(context):
    user = context['request'].user

    return {
        'user': str(user),
        'is_superuser': user.is_superuser,
        'username': user.username,
    }