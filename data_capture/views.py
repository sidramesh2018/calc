from django.shortcuts import render
from django.template import RequestContext
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from . import forms


@login_required
def step_1(request):
    if request.method == 'GET':
        form = forms.Step1Form()
    elif request.method == 'POST':
        form = forms.Step1Form(request.POST, request.FILES)

        if form.is_valid():
            # TODO: Store the cleaned price list data in session state
            # or something similar.

            redirect_url = reverse('data_capture:step_2')
            if request.is_ajax():
                return JsonResponse({'redirect_url': redirect_url})
            return HttpResponseRedirect(redirect_url)

    ctx = {
        'step_number': 1,
        'form': form
    }

    if request.is_ajax():
        return JsonResponse({
            'form_html': render_to_string(
                'data_capture/step_1_form.html',
                RequestContext(request, ctx)
            )
        })

    return render(request, 'data_capture/step_1.html', ctx)


@login_required
def step_2(request):
    # TODO: Retrieve price list from session state (or whereever we put
    # it at end of step 1) and show validation information. If the
    # session state doesn't exist or is invalid, redirect the user to
    # step 1.

    return render(request, 'data_capture/step_2.html', {
        'step_number': 2
    })


@login_required
def step_3(request):
    # TODO: Create the form for the user to input information about the
    # contract details.

    return render(request, 'data_capture/step_3.html', {
        'step_number': 3
    })


@login_required
def step_4(request):
    return render(request, 'data_capture/step_4.html', {
        'step_number': 4
    })
