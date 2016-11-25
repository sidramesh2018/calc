from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.utils.crypto import get_random_string


def about(request):
    return render(request, 'about.html', {
        'current_selected_tab': 'about'
    })


def index(request):
    csp_nonce = get_random_string(length=10)
    response = render(request, 'index.html', {
        'csp_nonce': mark_safe('nonce="{}"'.format(csp_nonce))
    })
    response['Content-Security-Policy'] = '; '.join([
        "default-src *",
        "script-src * 'unsafe-inline' 'nonce-{}'".format(csp_nonce),
        "style-src * 'unsafe-inline'",
        "img-src * data:",
    ])
    return response
