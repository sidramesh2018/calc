from django import template
from django.contrib.staticfiles.storage import staticfiles_storage

from hourglass.site_utils import absolutify_url


register = template.Library()


@register.simple_tag()
def absolute_static(url):
    '''
    This is like the {% static %} template tag, but it ensures that
    the returned URL is absolute, so that it can be included in an
    email.

    Unlike the {% static %} tag, however, it doesn't allow the URL
    to be assigned to a context variable.
    '''

    return absolutify_url(staticfiles_storage.url(url))


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
