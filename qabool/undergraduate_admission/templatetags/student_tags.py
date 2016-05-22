from django import template

register = template.Library()


@register.inclusion_tag('undergraduate_admission/_student_info_commands.html', takes_context=True)
def student_info_commands(context):
    user = context['request'].user
    phase = user.get_student_phase()
    can_withdraw = phase == 'PARTIALLY-ADMITTED' or phase == 'ADMITTED'
    can_print_docs = phase == 'ADMITTED'
    can_confirm = phase == 'PARTIALLY-ADMITTED'
    has_pic = phase == 'PARTIALLY-ADMITTED' or phase == 'ADMITTED'

    return {
        'user': user,
        'can_withdraw': can_withdraw,
        'can_print_docs': can_print_docs,
        'can_confirm': can_confirm,
        'has_pic': has_pic
    }