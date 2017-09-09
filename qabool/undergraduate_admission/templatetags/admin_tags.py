from django import template
from django.core.exceptions import ObjectDoesNotExist

from undergraduate_admission.models import AdmissionSemester

register = template.Library()


@register.inclusion_tag('undergraduate_admission/admin/_admin_commands.html', takes_context=True)
def admin_commands(context):
    user = context['request'].user
    is_verifier = 'Verifier' in user.groups.all() or user.is_superuser
    is_tarifi_admin = user.is_superuser \
                      or 'Tarifi Admin' in user.groups.all() \
                      or 'Tarifi Super Admin' in user.groups.all()

    return {
        'user': str(user),
        'is_superuser': user.is_superuser,
        'is_verifier': is_verifier,
        'is_tarifi_admin': is_tarifi_admin,
        'username': user.username,
        'groups': user.groups.all(),
    }
