import json
import urllib.parse

from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect, render
from django.http import HttpResponseBadRequest
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.utils.http import is_safe_url
from django.utils.safestring import mark_safe
from django.utils.html import escape

from .. import forms
from ..models import SubmittedPriceList
from ..decorators import handle_cancel
from ..schedules import registry
from ..management.commands.initgroups import PRICE_LIST_UPLOAD_PERMISSION
from .common import add_generic_form_error, Steps
from frontend import ajaxform


steps = Steps(
    template_format='data_capture/price_list/step_{}.html',
    extra_ctx_vars={
        'current_selected_tab': 'upload_price_data'
    }
)


def build_url(viewname, **kwargs):
    '''
    Build a URL using the given view name and the given query string
    arguments, returning the result:

        >>> build_url('data_capture:step_4', a='1')
        '/data-capture/step/4?a=1'

    Any keyword arguments that are `None` will be excluded, though:

        >>> build_url('data_capture:step_4', a=None)
        '/data-capture/step/4'
    '''

    url = reverse(viewname)
    query = [
        (key, kwargs[key]) for key in kwargs
        if kwargs[key] is not None
    ]
    if not query:
        return url
    return '{}?{}'.format(url, urllib.parse.urlencode(query))


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


def get_deserialized_gleaned_data(request):
    '''
    Gets 'gleaned_data' from session and uses the registry to deserialize
    it. Returns None if 'gleaned_data' is not in session.
    '''
    serialized_gleaned_data = get_nested_item(request.session, (
        'data_capture:price_list', 'gleaned_data'))
    if serialized_gleaned_data:
        return registry.deserialize(serialized_gleaned_data)
    return None


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
        elif form.has_existing_contract_number_error():
            contract_number = request.POST['contract_number']
            latest = SubmittedPriceList.get_latest_by_contract_number(
                contract_number)
            details_url = reverse('data_capture:price_list_details',
                                  kwargs={'id': latest.pk})
            msg = mark_safe(
                "We found an existing price list for contract number {}.</br>"
                "If you'd like, you may "
                "<a href='{}'>see its details</a>.".format(
                    escape(contract_number), details_url))
            messages.add_message(request, messages.ERROR, msg)
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
        'form': form,
        'step_1_data': get_step_form_from_session(1, request)
    })


@steps.step
@login_required
@permission_required(PRICE_LIST_UPLOAD_PERMISSION, raise_exception=True)
@require_http_methods(["GET", "POST"])
@handle_cancel
def step_3(request, step):
    if get_step_form_from_session(2, request) is None:
        return redirect('data_capture:step_2')

    session_pl = request.session['data_capture:price_list']
    step_1_data = get_step_form_from_session(1, request).cleaned_data
    schedule_class = step_1_data['schedule_class']

    if request.method == 'GET':

        gleaned_data = get_deserialized_gleaned_data(request)
        force_show = (request.GET.get('force') == 'on')

        if not force_show and gleaned_data and gleaned_data.valid_rows:
            # If gleaned_data is in session and has valid rows
            # show the step 3 interstitial
            return redirect('data_capture:step_3_data')

        form = forms.Step3Form(schedule=step_1_data['schedule'])
    else:  # POST
        gleaned_data = get_deserialized_gleaned_data(request)

        form = forms.Step3Form(
            request.POST,
            request.FILES,
            schedule=step_1_data['schedule']
        )

        if form.is_valid():
            gleaned_data = form.cleaned_data['gleaned_data']

            session_pl['gleaned_data'] = registry.serialize(gleaned_data)
            request.session.modified = True

            if gleaned_data.invalid_rows:
                return ajaxform.redirect(request, 'data_capture:step_3_errors')
            return ajaxform.redirect(request, 'data_capture:step_4')
        else:
            add_generic_form_error(request, form)

    return ajaxform.render(
        request,
        context=step.context({
            'form': form,
            'upload_example': schedule_class.render_upload_example(request)
        }),
        template_name=step.template_name,
        ajax_template_name='data_capture/price_list/upload_form.html',
    )


@login_required
@permission_required(PRICE_LIST_UPLOAD_PERMISSION, raise_exception=True)
@handle_cancel
@require_http_methods(["GET"])
def step_3_data(request):
    step = steps.get_step_renderer(3)
    gleaned_data = get_deserialized_gleaned_data(request)

    if not gleaned_data or not gleaned_data.valid_rows:
        return redirect('data_capture:step_3')

    step_1_form = get_step_form_from_session(1, request)

    preferred_schedule = step_1_form.cleaned_data['schedule_class']

    return render(request,
                  'data_capture/price_list/step_3_data.html',
                  step.context({
                    'gleaned_data': gleaned_data,
                    'is_preferred_schedule': isinstance(gleaned_data,
                                                        preferred_schedule),
                    'preferred_schedule_title': preferred_schedule.title,
                  }))


@login_required
@permission_required(PRICE_LIST_UPLOAD_PERMISSION, raise_exception=True)
@handle_cancel
@require_http_methods(["GET"])
def step_3_errors(request):
    step = steps.get_step_renderer(3)

    gleaned_data = get_deserialized_gleaned_data(request)

    if gleaned_data is None:
        return redirect('data_capture:step_3')

    step_1_form = get_step_form_from_session(1, request)

    preferred_schedule = step_1_form.cleaned_data['schedule_class']

    form = forms.Step3Form(schedule=step_1_form.cleaned_data['schedule'])

    return render(request,
                  'data_capture/price_list/step_3_errors.html',
                  step.context({
                    'form': form,
                    'gleaned_data': gleaned_data,
                    'is_preferred_schedule': isinstance(gleaned_data,
                                                        preferred_schedule),
                    'preferred_schedule_title': preferred_schedule.title,
                  }))


@steps.step
@login_required
@permission_required(PRICE_LIST_UPLOAD_PERMISSION, raise_exception=True)
@require_http_methods(["GET", "POST"])
@handle_cancel
@transaction.atomic
def step_4(request, step):
    gleaned_data = get_deserialized_gleaned_data(request)

    if gleaned_data is None:
        return redirect('data_capture:step_3')

    if request.method == 'GET' and not gleaned_data.valid_rows:
        return redirect('data_capture:step_3')

    session_pl = request.session['data_capture:price_list']
    step_1_form = get_step_form_from_session(1, request)
    step_2_form = get_step_form_from_session(2, request)

    pl_details = {
        'preferred_schedule': step_1_form.cleaned_data['schedule_class'],
        'contract_number': step_1_form.cleaned_data['contract_number'],
        'vendor_name': step_2_form.cleaned_data['vendor_name'],
        'is_small_business': step_2_form.cleaned_data['is_small_business'],
        'contractor_site': step_2_form.cleaned_data['contractor_site'],
        'contract_start': step_2_form.cleaned_data['contract_start'],
        'contract_end': step_2_form.cleaned_data['contract_end'],
        'escalation_rate': step_2_form.cleaned_data['escalation_rate'],
    }

    show_edit_form = (request.GET.get('show_edit_form') == 'on')

    if request.method == 'POST':
        if not gleaned_data.valid_rows:
            # Our UI never should've let the user issue a request
            # like this.
            return HttpResponseBadRequest()
        form = forms.Step4Form(request.POST)
    else:
        form = forms.Step4Form.from_post_data_subsets(
            session_pl['step_1_POST'],
            session_pl['step_2_POST']
        )

    prev_url = request.GET.get('prev')
    if not is_safe_url(prev_url):
        prev_url = None

    step_4_without_edit_url = build_url('data_capture:step_4',
                                        prev=prev_url)
    step_4_with_edit_url = build_url('data_capture:step_4',
                                     prev=prev_url,
                                     show_edit_form='on')

    if request.method == 'POST':
        if form.is_valid():
            if 'save-changes' in request.POST:
                # There's not a particularly easy way to separate one
                # step's fields from another, but fortunately that's OK
                # because Django's Form constructors take only the POST
                # data they need, and ignore the rest.
                session_pl['step_1_POST'] = request.POST
                session_pl['step_2_POST'] = request.POST

                # Changing the value of a subkey doesn't cause the session to
                # save, so do it manually.
                request.session.modified = True

                return redirect(step_4_without_edit_url)
            else:
                price_list = form.save(commit=False)

                price_list.submitter = request.user
                price_list.serialized_gleaned_data = json.dumps(
                    session_pl['gleaned_data'])

                # We always want to explicitly set the schedule to the
                # one that the gleaned data is part of, in case we gracefully
                # fell back to a schedule other than the one the user chose.
                price_list.schedule = registry.get_classname(gleaned_data)

                price_list.status = SubmittedPriceList.STATUS_NEW
                price_list.status_changed_at = timezone.now()
                price_list.status_changed_by = request.user

                price_list.save()
                gleaned_data.add_to_price_list(price_list)

                del request.session['data_capture:price_list']

                return redirect('data_capture:step_5')
        else:
            add_generic_form_error(request, form)
            show_edit_form = True

    return step.render(request, {
        'show_edit_form': show_edit_form,
        'form': form,
        'step_4_with_edit_url': step_4_with_edit_url,
        'step_4_without_edit_url': step_4_without_edit_url,
        'prev_url': prev_url,
        'gleaned_data': gleaned_data,
        'price_list': pl_details,
        'is_preferred_schedule': isinstance(gleaned_data,
                                            pl_details['preferred_schedule']),
        'preferred_schedule_title': pl_details['preferred_schedule'].title,
    })


@steps.step
@login_required
@permission_required(PRICE_LIST_UPLOAD_PERMISSION, raise_exception=True)
def step_5(request, step):
    return step.render(request)
