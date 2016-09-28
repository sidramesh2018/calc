from django import template


register = template.Library()


@register.simple_tag(takes_context=True)
def fieldset(context, field):
    '''
    This template tag makes it easy to render form fields as
    <fieldset> elements.
    '''

    t = context.template.engine.get_template('frontend/fieldset.html')

    return t.render(template.Context({
        'field': field,
    }))
