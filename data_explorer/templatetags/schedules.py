from django import template

register = template.Library()


@register.assignment_tag
def get_schedules():
    """ Returns the list of SIN and schedule names. Each dictionary returned
    contains three keys:

        SIN - the schedule number
        name - the human readable name
    """
    return [{
        'SIN': 520,
        'name': 'Legacy FABS'
    }, {
        'SIN': 541,
        'name': 'Legacy AIMS'
    }, {
        'SIN': 73802,
        'name': 'Legacy Language'
    }, {
        'SIN': 871,
        'name': 'Legacy PES'
    }, {
        'SIN': 874,
        'name': 'Legacy MOBIS'
    }, {
        'SIN': 87405,
        'name': 'Legacy Logistics'
    }, {
        'SIN': 899,
        'name': 'Legacy Environmental'
    }, {
        'SIN': 132,
        'name': 'IT 70'
    }]
