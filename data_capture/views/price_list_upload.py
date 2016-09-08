import json
from datetime import datetime
from functools import wraps
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .. import forms
from ..decorators import handle_cancel
from ..schedules import registry
from .common import add_generic_form_error
from frontend import ajaxform


def gleaned_data_required(f):
    @wraps(f)
    def wrapper(request):
        try:
            d = request.session['data_capture:price_list']['gleaned_data']
        except:
            return redirect('data_capture:step_3')

        return f(request, registry.deserialize(d))
    return wrapper


@login_required
def step_1(request):
    if request.method == 'GET':
        form = forms.Step1Form()
    elif request.method == 'POST':
        form = forms.Step1Form(request.POST)
        if form.is_valid():
            # Clear out request.session if it previously existed
            if 'data_capture:price_list' in request.session:
                del request.session['data_capture:price_list']

            request.session['data_capture:price_list'] = {
                'contract_number': request.POST['contract_number'],
                'vendor_name': request.POST['vendor_name'],
                'schedule': request.POST['schedule']
            }
            return redirect('data_capture:step_2')

        else:
            add_generic_form_error(request, form)

    return render(request, 'data_capture/price_list/step_1.html', {
            'step_number': 1,
            'form': form,
        })


@handle_cancel
@login_required
def step_2(request):
    def ymd(date_input):
        return date_input.strftime("%Y-%m-%d")
    # Redirect back to step 1 if we don't have data
    if 'contract_number' not in request.session.get('data_capture:price_list',
                                                    {}):
        return redirect('data_capture:step_1')

    if request.method == 'GET':
        form = forms.Step2Form()
    elif request.method == 'POST':
        form = forms.Step2Form(request.POST)
        if form.is_valid():
            session_data = request.session['data_capture:price_list']
            session_data.update({
                'is_small_business': form.cleaned_data['is_small_business'],
                'contractor_site': form.cleaned_data['contractor_site'],
                'contract_year': form.cleaned_data['contract_year'],
                'contract_start': ymd(form.cleaned_data['contract_start']),
                'contract_end': ymd(form.cleaned_data['contract_end'])
            })

            # Changing the value of a subkey doesn't cause the session to save,
            # so do it manually
            request.session.modified = True

            return redirect('data_capture:step_3')
        else:
            add_generic_form_error(request, form)

    return render(request, 'data_capture/price_list/step_2.html', {
        'step_number': 2,
        'form': form
    })


@handle_cancel
@login_required
def step_3(request):
    if 'data_capture:price_list' not in request.session:
        return redirect('data_capture:step_1')
    else:
        if request.method == 'GET':
            form = forms.Step3Form()
        elif request.method == 'POST':
            sked = request.session['data_capture:price_list']['schedule']
            posted_data = dict(
                request.POST,
                schedule=sked)
            form = forms.Step3Form(posted_data, request.FILES)

            if form.is_valid():
                request.session['data_capture:price_list']['gleaned_data'] = \
                    registry.serialize(form.cleaned_data['gleaned_data'])

                request.session.modified = True

                return ajaxform.redirect(request, 'data_capture:step_4')
            else:
                add_generic_form_error(request, form)

        return ajaxform.render(
            request,
            context={
                'step_number': 3,
                'form': form
            },
            template_name='data_capture/price_list/step_3.html',
            ajax_template_name='data_capture/price_list/upload_form.html',
        )


@login_required
@gleaned_data_required
@handle_cancel
def step_4(request, gleaned_data):
    if not gleaned_data.valid_rows:
        return redirect('data_capture:step_3')
    else:
        preferred_schedule = registry.get_class(
            request.session['data_capture:price_list']['schedule']
        )
        if request.method == 'POST':
            form = forms.Step4Form(request.POST)
            if form.is_valid():
                sesh_data = request.session['data_capture:price_list']
                price_list = form.save(commit=False)
                price_list.contract_start = \
                    datetime.strptime(sesh_data['contract_start'], "%Y-%m-%d")
                price_list.contract_end = \
                    datetime.strptime(sesh_data['contract_end'], "%Y-%m-%d")
                price_list.submitter = request.user
                price_list.serialized_gleaned_data = json.dumps(
                    sesh_data['gleaned_data'])
                price_list.save()
                gleaned_data.add_to_price_list(price_list)
                return redirect('data_capture:step_5')

    return render(request, 'data_capture/price_list/step_4.html', {
        'step_number': 4,
        'gleaned_data': gleaned_data,
        'price_list': request.session['data_capture:price_list'],
        'is_preferred_schedule': isinstance(gleaned_data, preferred_schedule),
        'preferred_schedule': preferred_schedule,
    })


@login_required
@gleaned_data_required
def step_5(request, gleaned_data):
    if gleaned_data.valid_rows:
        del request.session['data_capture:price_list']
    else:
        # The user may have manually changed the URL or something to
        # get here. Push them back to the last step.
        return redirect('data_capture:step_4')

    return render(request, 'data_capture/price_list/step_5.html', {
        'step_number': 5
    })
