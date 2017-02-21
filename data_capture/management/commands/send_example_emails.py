from django.utils import timezone

import djclick as click

from data_capture import email


pl_ctx = {
    'price_list': {
        'created_at': timezone.now(),
        'contract_number': 'GS-12-Example',
        'get_schedule_title': 'Fake Schedule',
        'vendor_name': 'Example Vendor, Inc.',
    },
    'details_link': 'https://example.com/price-list/details',
}

EXAMPLES = [
    dict(
        subject='Example Price List Approved',
        template='data_capture/email/price_list_approved.html',
        ctx=pl_ctx
    ),
    dict(
        subject='Example Price List Rejected',
        template='data_capture/email/price_list_rejected.html',
        ctx=pl_ctx
    ),
    dict(
        subject='Example Price List Retired',
        template='data_capture/email/price_list_retired.html',
        ctx=pl_ctx
    ),
    dict(
        subject='Example Bulk Upload Succeeded',
        template='data_capture/email/bulk_upload_succeeded.html',
        ctx={
                'upload_source': {
                    'id': 2,
                    'submitter': {'email': 'example_admin@example.com'},
                    'created_at': timezone.now(),
                },
                'num_contracts': 50123,
                'num_bad_rows': 25,
        }
    ),
    dict(
        subject='Example Bulk Upload Failed',
        template='data_capture/email/bulk_upload_failed.html',
        ctx={
                'upload_source': {
                    'id': 2,
                    'submitter': {'email': 'example_admin@example.com'},
                    'created_at': timezone.now(),
                },
                'r10_upload_link': 'https://example.com/r10_bulk_upload',
                'traceback': 'error traceback'
            }
    ),
    dict(
        subject='Example Price List Review Reminder',
        template='data_capture/email/approval_reminder.html',
        ctx={
                'unreviewed_url': 'https://example.com/unreviewed_price_lists',
            }
    )
]

@click.command()
@click.argument('to', default='user@example.com')
def command(to):
    '''
    Send examples of all the email templates in the Data Capture application.
    '''

    for example in EXAMPLES:
        kwargs = {'to': [to]}
        kwargs.update(example)
        email.send_mail(**kwargs)
