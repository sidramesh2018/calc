import json
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required, permission_required

from .. import forms
from ..decorators import handle_cancel
from ..schedules import registry
from ..management.commands.initgroups import PRICE_LIST_UPLOAD_PERMISSION
from .common import add_generic_form_error, Steps
from frontend import ajaxform


steps = Steps(
    template_format='data_capture/price_list/step_{}.html',
)


def get_nested_item(obj, keys, default=None):
    '''
    Get a nested item from a nested structure of dictionary-like objects,
    returning a default value if any expected keys are not present.

    Examples:

        >>> d = {'foo': {'bar': 'baz'}}
        >>> get_nested_item(d, ('foo', 'bar'))
        'baz'
        >>> get_nested_item(d, ('foo', 'blarg'))
    '''

    key = keys[0]
    if key not in obj:
        return default
    if len(keys) > 1:
        return get_nested_item(obj[key], keys[1:], default)
    return obj[key]


def get_step_form_from_session(step_number, request, **kwargs):
    '''
    Bring back the given Form instance for a step from the
    request session.  Returns None if the step hasn't been completed yet.

    Any keyword arguments are passed on to the Form constructor.
    '''

    cls = getattr(forms, 'Step{}Form'.format(step_number))
    post_data = get_nested_item(request.session, (
        'data_capture:price_list',
        'step_{}_POST'.format(step_number)
    ))
    if post_data is None:
        return None
    form = cls(post_data, **kwargs)
    if not form.is_valid():
        raise AssertionError(
            'invalid step {} data in session'.format(step_number)
        )
    return form


@steps.step
@login_required
@permission_required(PRICE_LIST_UPLOAD_PERMISSION, raise_exception=True)
@require_http_methods(["GET", "POST"])
def step_1(request, step):
    if request.method == 'GET':
        form = forms.Step1Form(data=get_nested_item(
            request.session,
            ('data_capture:price_list', 'step_1_POST')
        ))
    else:
        form = forms.Step1Form(request.POST)
        if form.is_valid():
            request.session['data_capture:price_list'] = {
                'step_1_POST': request.POST,
            }
            return redirect('data_capture:step_2')

        else:
            add_generic_form_error(request, form)

    return step.render(request, {
        'form': form,
    })


@steps.step
@login_required
@permission_required(PRICE_LIST_UPLOAD_PERMISSION, raise_exception=True)
@require_http_methods(["GET", "POST"])
@handle_cancel
def step_2(request, step):
    # Redirect back to step 1 if we don't have data
    if get_step_form_from_session(1, request) is None:
        return redirect('data_capture:step_1')

    if request.method == 'GET':
        form = forms.Step2Form(data=get_nested_item(
            request.session,
            ('data_capture:price_list', 'step_2_POST')
        ))
    else:
        form = forms.Step2Form(request.POST)
        if form.is_valid():
            session_data = request.session['data_capture:price_list']
            session_data['step_2_POST'] = request.POST

            # Changing the value of a subkey doesn't cause the session to save,
            # so do it manually
            request.session.modified = True

            return redirect('data_capture:step_3')
        else:
            add_generic_form_error(request, form)

    return step.render(request, {
        'form': form
    })


@steps.step
@login_required
@permission_required(PRICE_LIST_UPLOAD_PERMISSION, raise_exception=True)
@require_http_methods(["GET", "POST"])
@handle_cancel
def step_3(request, step):
    if get_step_form_from_session(2, request) is None:
        return redirect('data_capture:step_2')
    else:
        session_pl = request.session['data_capture:price_list']
        step_1_data = get_step_form_from_session(1, request).cleaned_data
        schedule_class = step_1_data['schedule_class']

        if request.method == 'GET':
            form = forms.Step3Form(schedule=step_1_data['schedule'])
        else:
            form = forms.Step3Form(
                request.POST,
                request.FILES,
                schedule=step_1_data['schedule']
            )

            if form.is_valid():
                session_pl['gleaned_data'] = \
                    registry.serialize(form.cleaned_data['gleaned_data'])

                request.session.modified = True

                return ajaxform.redirect(request, 'data_capture:step_4')
            else:
                add_generic_form_error(request, form)

        return ajaxform.render(
            request,
            context=step.context({
                'form': form,
                'upload_example': schedule_class.render_upload_example()
            }),
            template_name=step.template_name,
            ajax_template_name='data_capture/price_list/upload_form.html',
        )


@steps.step
@login_required
@permission_required(PRICE_LIST_UPLOAD_PERMISSION, raise_exception=True)
@handle_cancel
def step_4(request, step):
    gleaned_data = get_nested_item(request.session, (
        'data_capture:price_list',
        'gleaned_data',
    ))

    if gleaned_data is None:
        return redirect('data_capture:step_3')

    gleaned_data = registry.deserialize(gleaned_data)

    session_pl = request.session['data_capture:price_list']
    step_1_form = get_step_form_from_session(1, request)

    preferred_schedule = step_1_form.cleaned_data['schedule_class']

    if request.method == 'POST':
        if not gleaned_data.valid_rows:
            # Our UI never should've let the user issue a request
            # like this.
            return HttpResponseBadRequest()
        price_list = step_1_form.save(commit=False)
        step_2_form = get_step_form_from_session(2, request,
                                                 instance=price_list)
        step_2_form.save(commit=False)

        price_list.submitter = request.user
        price_list.serialized_gleaned_data = json.dumps(
            session_pl['gleaned_data'])

        # We always want to explicitly set the schedule to the
        # one that the gleaned data is part of, in case we gracefully
        # fell back to a schedule other than the one the user chose.
        price_list.schedule = registry.get_classname(gleaned_data)

        price_list.save()
        gleaned_data.add_to_price_list(price_list)

        del request.session['data_capture:price_list']

        return redirect('data_capture:step_5')

    return step.render(request, {
        'gleaned_data': gleaned_data,
        'is_preferred_schedule': isinstance(gleaned_data, preferred_schedule),
        'preferred_schedule_title': preferred_schedule.title,
    })


@steps.step
@login_required
@permission_required(PRICE_LIST_UPLOAD_PERMISSION, raise_exception=True)
def step_5(request, step):
    return step.render(request)
