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
        'name': 'Formerly FABS'
    }, {
        'SIN': 541,
        'name': 'Formerly AIMS'
    }, {
        'SIN': 73802,
        'name': 'Formerly Language'
    }, {
        'SIN': 871,
        'name': 'Formerly PES'
    }, {
        'SIN': 874,
        'name': 'Formerly MOBIS'
    }, {
        'SIN': 87405,
        'name': 'Formerly Logistics'
    }, {
        'SIN': 899,
        'name': 'Formerly Environmental'
    }, {
        'SIN': 132,
        'name': 'IT 70'
    }]
