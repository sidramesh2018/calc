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
    script_src = ' '.join([
        "'self'",
        "*.googleapis.com",
        "dap.digitalgov.gov",
        "www.google-analytics.com",
        "ethn.io",
        # Browsers that don't support CSP v2 need this to work.
        "'unsafe-inline'",
        # For browsers that *do* support CSP v2, the following will
        # override our earlier 'unsafe-inline' directive.
        "'nonce-{}'".format(csp_nonce)
    ])
    response['Content-Security-Policy'] = '; '.join([
        "default-src *",
        "script-src {}".format(script_src),
        "style-src * 'unsafe-inline'",
        "img-src * data:",
    ])
    return response
