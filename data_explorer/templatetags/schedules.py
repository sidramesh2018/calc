from django import template

register = template.Library()


@register.assignment_tag
def get_schedules():
    """ Returns the list of SIN and schedule names. Each dictionary returned
    contains three keys:

        SIN - the schedule number
        schedule - the schedule name.
        name - the human readable name
        name - the human readable name
    """
    return [{
        'SIN': 520,
        'schedule': 'FABS',
        'name': 'Legacy FABS'
    }, {
        'SIN': 541,
        'schedule': 'AIMS',
        'name': 'Legacy AIMS'
    }, {
        'SIN': 73802,
        'schedule': 'Language Services',
        'name': 'Legacy Language'
    }, {
        'SIN': 871,
        'schedule': 'PES',
        'name': 'Legacy PES'
    }, {
        'SIN': 874,
        'schedule': 'MOBIS',
        'name': 'Legacy MOBIS'
    }, {
        'SIN': 87405,
        'schedule': 'Logistics',
        'name': 'Legacy Logistics'
    }, {
        'SIN': 899,
        'schedule': 'Environmental',
        'name': 'Legacy Environmental'
    }, {
        'SIN': 132,
        'schedule': 'IT Schedule 70',
        'name': 'IT 70'
    }]
