from django import template
from django.utils.formats import localize
from pytz import timezone

register = template.Library()


@register.filter
def tz_timestamp(value, tz_name="US/Eastern"):
    '''
    This template filter formats the given timezone-aware datetime into
    a more readable format (ex: "Jan 1, 2015, 1:55 p.m. (EST)"),
    localized to the timezone specified by tz_name.
    '''
    try:
        tz = timezone(tz_name)
        timestamp = value.astimezone(tz)
        return "{} ({})".format(localize(timestamp), timestamp.tzname())
    except (AttributeError, ValueError):
        # just return the original value
        return value
