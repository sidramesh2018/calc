from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string


def redirect(request, target):
    redirect_url = reverse(target)
    if request.is_ajax():
        return JsonResponse({'redirect_url': redirect_url})
    return HttpResponseRedirect(redirect_url)


def render(request, context, template_name, ajax_template_name):
    final_context = RequestContext(request, context)

    if request.is_ajax():
        return JsonResponse({
            'form_html': render_to_string(ajax_template_name, final_context)
        })

    return HttpResponse(render_to_string(template_name, final_context))
