from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.conf import settings
from django.template.defaultfilters import pluralize

from .models import SubmittedPriceList


class EmailResult():
    '''
    Simple class to hold result data from email sending functions
    '''
    def __init__(self, was_successful, context=None):
        self.was_successful = was_successful
        self.context = context or {}


def price_list_approved(price_list):
    ctx = {
        'price_list': price_list
    }
    if price_list.status is not SubmittedPriceList.STATUS_APPROVED:
        raise AssertionError('price_list.status must be STATUS_APPROVED')

    result = send_mail(
        subject='CALC Price List Approved',
        message=render_to_string(
            'data_capture/email/price_list_approved.txt',
            ctx),
        from_email=settings.SYSTEM_EMAIL_ADDRESS,
        recipient_list=[price_list.submitter.email]
    )
    return EmailResult(
        was_successful=result is 1,
        context=ctx
    )


def price_list_retired(price_list):
    ctx = {
        'price_list': price_list
    }
    if price_list.status is not SubmittedPriceList.STATUS_RETIRED:
        raise AssertionError('price_list.status must be STATUS_RETIRED')
    result = send_mail(
        subject='CALC Price List Retired',
        message=render_to_string(
            'data_capture/email/price_list_retired.txt',
            ctx),
        from_email=settings.SYSTEM_EMAIL_ADDRESS,
        recipient_list=[price_list.submitter.email]
    )
    return EmailResult(
        was_successful=result is 1,
        context=ctx
    )


def price_list_rejected(price_list):
    ctx = {
        'price_list': price_list
    }
    result = send_mail(
        subject='CALC Price List Rejected',
        message=render_to_string(
            'data_capture/email/price_list_rejected.txt',
            ctx),
        from_email=settings.SYSTEM_EMAIL_ADDRESS,
        recipient_list=[price_list.submitter.email]
    )
    if price_list.status is not SubmittedPriceList.STATUS_REJECTED:
        raise AssertionError('price_list.status must be STATUS_REJECTED')
    return EmailResult(
        was_successful=result is 1,
        context=ctx
    )


def bulk_upload_succeeded(upload_source, num_contracts, num_bad_rows):
    ctx = {
        'upload_source': upload_source,
        'num_contracts': num_contracts,
        'num_bad_rows': num_bad_rows,
    }
    result = send_mail(
        subject='CALC Region 10 bulk data results - upload #%d' % (
            upload_source.id,
        ),
        message=render_to_string(
            'data_capture/email/bulk_upload_succeeded.txt',
            ctx
        ),
        from_email=settings.SYSTEM_EMAIL_ADDRESS,
        recipient_list=[upload_source.submitter.email]
    )
    return EmailResult(
        was_successful=result is 1,
        context=ctx
    )


def bulk_upload_failed(upload_source, traceback):
    ctx = {
        'upload_source': upload_source,
        'traceback': traceback,
    }
    result = send_mail(
        subject='CALC Region 10 bulk data results - upload #%d' % (
            upload_source.id,
        ),
        message=render_to_string(
            'data_capture/email/bulk_upload_failed.txt',
            ctx
        ),
        from_email=settings.SYSTEM_EMAIL_ADDRESS,
        recipient_list=[upload_source.submitter.email]
    )
    return EmailResult(
        was_successful=result is 1,
        context=ctx
    )


def approval_reminder(count_unreviewed):
    ctx = {
        'count_unreviewed': count_unreviewed
    }
    superusers = User.objects.filter(is_superuser=True)
    recipients = [s.email for s in superusers if s.email]
    result = send_mail(
        subject='CALC Reminder - {} price list{} not reviewed'.format(
            count_unreviewed, pluralize(count_unreviewed)),
        message=render_to_string(
            'data_capture/email/approval_reminder.txt',
            ctx
        ),
        from_email=settings.SYSTEM_EMAIL_ADDRESS,
        recipient_list=recipients
    )
    return EmailResult(
        was_successful=result is 1,  # or count of superusers
        context=ctx
    )
