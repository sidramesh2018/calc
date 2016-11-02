import json

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required

from ..schedules import registry
from ..models import SubmittedPriceList
from ..management.commands.initgroups import PRICE_LIST_UPLOAD_PERMISSION


@login_required
@permission_required(PRICE_LIST_UPLOAD_PERMISSION, raise_exception=True)
def list_price_lists(request):
    '''
    This view lists a user's SubmittedPriceLists, segmented into lists based
    on the model's status.
    '''
    approved_price_lists = SubmittedPriceList.objects.filter(
        submitter=request.user,
        status=SubmittedPriceList.STATUS_APPROVED).order_by(
            '-status_changed_at')

    new_price_lists = SubmittedPriceList.objects.filter(
        submitter=request.user,
        status=SubmittedPriceList.STATUS_NEW).order_by(
            '-status_changed_at')

    rejected_price_lists = SubmittedPriceList.objects.filter(
        submitter=request.user,
        status=SubmittedPriceList.STATUS_REJECTED).order_by(
            '-status_changed_at')

    unapproved_price_lists = SubmittedPriceList.objects.filter(
        submitter=request.user,
        status=SubmittedPriceList.STATUS_UNAPPROVED).order_by(
            '-status_changed_at')

    return render(request, 'price_lists/list.html', {
        'approved_price_lists': approved_price_lists,
        'new_price_lists': new_price_lists,
        'rejected_price_lists': rejected_price_lists,
        'unapproved_price_lists': unapproved_price_lists,
    })


@login_required
@permission_required(PRICE_LIST_UPLOAD_PERMISSION, raise_exception=True)
def price_list_details(request, id):
    '''
    This view shows all the details of a SubmittedPriceList model.
    Note that any logged-in user with the PRICE_LIST_UPLOAD_PERMISSION (so
    Contract Officers and above) can view the page for ANY SubmittedPriceList,
    not just the ones they've submitted.
    '''
    price_list = get_object_or_404(SubmittedPriceList, pk=id)

    gleaned_data = registry.deserialize(
        json.loads(price_list.serialized_gleaned_data))

    return render(request, 'price_lists/details.html', {
        'price_list': price_list,
        'gleaned_data': gleaned_data,
    })
