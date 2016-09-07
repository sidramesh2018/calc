from django import template

register = template.Library()


@register.assignment_tag
def get_schedules():
    """ Returns the list of SIN and schedule names """
    return [{
        'SIN': 520,
        'name': 'FABS'
    }, {
        'SIN': 541,
        'name': 'AIMS'
    }, {
        'SIN': 73802,
        'name': 'Language'
    }, {
        'SIN': 871,
        'name': 'PES'
    }, {
        'SIN': 874,
        'name': 'MOBIS'
    }, {
        'SIN': 87405,
        'name': 'Logistics'
    }, {
        'SIN': 899,
        'name': 'Environmental'
    }, {
        'SIN': 132,
        'name': 'IT 70'
    }]
