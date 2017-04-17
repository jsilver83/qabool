from django import template
from django.core.cache import cache

from undergraduate_admission.models import ImportantDateSidebar

register = template.Library()


@register.inclusion_tag('undergraduate_admission/_important_dates.html', takes_context=True)
def important_dates(context):
    # cache if important dates is not change for 15 mins
    if cache.get('important_dates') is None:
        important_dates = ImportantDateSidebar.objects.filter(show=True)
        cache.set('important_dates', important_dates, 15 * 60)
    else:
        important_dates = cache.get('important_dates')

    return {
        'important_dates': important_dates,
    }
