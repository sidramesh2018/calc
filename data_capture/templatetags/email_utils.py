from django import template


register = template.Library()


@register.simple_tag(takes_context=True)
def cta(context, url, text):
    '''
    A call-to-action button for HTML emails.
    '''

    if not context.get('is_html_email'):
        raise Exception('This tag should only be used in HTML emails')

    t = context.template.engine.get_template('email/cta.html')

    return t.render(template.Context({
        'url': url,
        'text': text,
    }))
