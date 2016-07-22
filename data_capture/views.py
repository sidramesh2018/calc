from functools import wraps
from django.conf import settings
from django.shortcuts import render, redirect
from django.template import RequestContext
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from . import forms
from .schedules import registry


@login_required
def step_1(request):
    if request.method == 'GET':
        form = forms.Step1Form()
    elif request.method == 'POST':
        form = forms.Step1Form(request.POST, request.FILES)

        if form.is_valid():
            request.session['data_capture:gleaned_data'] = \
                registry.serialize(form.cleaned_data['gleaned_data'])

            redirect_url = reverse('data_capture:step_2')
            if request.is_ajax():
                return JsonResponse({'redirect_url': redirect_url})
            return HttpResponseRedirect(redirect_url)

    ctx = {
        'step_number': 1,
        'form': form,
        'DEBUG': settings.DEBUG
    }

    if request.is_ajax():
        return JsonResponse({
            'form_html': render_to_string(
                'data_capture/step_1_form.html',
                RequestContext(request, ctx)
            )
        })

    return render(request, 'data_capture/step_1.html', ctx)


def gleaned_data_required(f):
    @wraps(f)
    def wrapper(request):
        d = request.session.get('data_capture:gleaned_data')

        if d is None:
            return redirect('data_capture:step_1')

        return f(request, registry.deserialize(d))
    return wrapper


@login_required
@gleaned_data_required
def step_2(request, gleaned_data):
    return render(request, 'data_capture/step_2.html', {
        'step_number': 2,
        'gleaned_data': gleaned_data
    })


@login_required
@gleaned_data_required
def step_3(request, gleaned_data):
    # TODO: Create the form for the user to input information about the
    # contract details.

    return render(request, 'data_capture/step_3.html', {
        'step_number': 3
    })


@login_required
@gleaned_data_required
def step_4(request, gleaned_data):
    return render(request, 'data_capture/step_4.html', {
        'step_number': 4
    })
