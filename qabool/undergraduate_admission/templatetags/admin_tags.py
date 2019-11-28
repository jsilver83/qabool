from django import template
from django.urls import reverse
from django.utils.html import format_html

from shared_app.utils import UserGroups

register = template.Library()


@register.inclusion_tag('undergraduate_admission/admin/_admin_commands.html', takes_context=True)
def admin_commands(context):
    user = context['request'].user
    is_verifier = 'Verifier' in user.groups.all() or user.is_superuser
    is_tarifi_admin = user.is_superuser or user.groups.filter(name=UserGroups.TARIFI_ADMIN).exists()
    is_tarifi_staff = user.is_superuser or user.groups.filter(name=UserGroups.TARIFI_STAFF).exists()

    return {
        'user': str(user),
        'is_superuser': user.is_superuser,
        'is_staff': user.is_staff,
        'is_verifier': is_verifier,
        'is_tarifi_admin': is_tarifi_admin,
        'is_tarifi_staff': is_tarifi_staff,
        'username': user.username,
        'groups': user.groups.all(),
    }


@register.simple_tag(takes_context=True)
def render_uploaded_file(context, file_type, student_instance):
    request = context['request']
    is_the_user_a_student = not (request.user.groups.all() or request.user.is_staff or request.user.is_superuser)
    file = getattr(student_instance, file_type)
    if file:
        if is_the_user_a_student:
            served_file_url = reverse('download_user_file', args=(file_type, student_instance.pk))
        else:
            served_file_url = reverse('download_user_file_admin', args=(file_type, student_instance.pk))
        served_file_url = request.build_absolute_uri(served_file_url)

        # to solve the problem of static content served with http and the browser refusing to embed it within secure
        # link https://qabool.kfupm.edu.sa/...
        if 'qabool.kfupm' in served_file_url:
            served_file_url = served_file_url.replace('http', 'https')

        if file.url.endswith('.pdf'):
            return format_html('<embed src="{url}" width="450" height="650" type="application/pdf"><br>'
                               '<a title="{title}" target="_blank" href="{url}">'
                               '<i class="fa fa-file" aria-hidden="true"></i> Download PDF</a>',
                               url=served_file_url,
                               title=file_type)
        else:
            return format_html('<a href="{url}" target="_blank">'
                               '<img class="img-popup" style="width: 100%" src="{url}" alt="{alt}" /></a>',
                               url=served_file_url,
                               alt=file_type)
