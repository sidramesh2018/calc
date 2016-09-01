from django.http import HttpResponseRedirect
from django.conf.urls import url
from django.views.decorators.http import require_POST


def is_js_enabled(request):
    return request.session.get('enable_js', True)


@require_POST
def enable_js(request):
    request.session['enable_js'] = True
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@require_POST
def disable_js(request):
    request.session['enable_js'] = False
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


urlpatterns = [
    url('^enable$', enable_js, name='enable'),
    url('^disable$', disable_js, name='disable'),
]
