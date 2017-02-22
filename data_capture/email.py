import re
import premailer
from django.core.mail import EmailMultiAlternatives, get_connection
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.template.defaultfilters import pluralize
from django.conf import settings

from frontend import email_css
from hourglass.site_utils import absolute_reverse
from .models import SubmittedPriceList


class EmailResult():
    '''
    Simple class to hold result data from email sending functions
    '''
    def __init__(self, was_successful, context=None):
        self.was_successful = was_successful
        self.context = context or {}


def collapse_and_strip_tags(text):
    '''
    Strips HTML tags and collapases newlines in the given string.

    Example:

    >>> collapse_and_strip_tags('\\n\\n<p>hi james</p>\\n\\n\\n')
    '\\nhi james\\n'
    '''
    return re.sub(r'\n+', '\n', strip_tags(text))


def render_mail(template, ctx):
    '''
    Render the given template with the given context for
    plaintext and HTML formats. This is done by rendering the
    template *twice* with slightly modified contexts:
    complementary `is_html_email` and `is_plaintext` variables
    are set to whatever mode is being rendered.

    Returns a (plaintext, html) string tuple representing the rendered
    template in each format.
    '''

    html_ctx = ctx.copy()
    html_ctx['is_html_email'] = True
    html_ctx['is_plaintext_email'] = False
    html_ctx['email_css'] = email_css

    html_message = render_to_string(template, html_ctx)
    html_message = premailer.transform(html_message)

    # TODO: This is a workaround for
    # https://github.com/18F/calc/issues/1409, need to figure
    # out the exact reason behind it.
    html_message = html_message.encode(
        'ascii', 'xmlcharrefreplace').decode('ascii')

    plaintext_ctx = ctx.copy()
    plaintext_ctx['is_html_email'] = False
    plaintext_ctx['is_plaintext_email'] = True

    plaintext_message = collapse_and_strip_tags(
        render_to_string(template, plaintext_ctx)
    )

    return (plaintext_message, html_message)


def send_mail(subject, to, template, ctx, reply_to=None):
    '''
    Django's convinience send_mail function does not allow
    specification of the reply-to header, so we instead use
    the underlying EmailMultiAlternatives class to send CALC emails.

    Returns an integer representing the number of emails sent (just like
    Django's send_mail does).
    '''
    connection = get_connection()

    plaintext_message, html_message = render_mail(template, ctx)

    msg = EmailMultiAlternatives(
        connection=connection,
        subject=subject,
        body=plaintext_message,
        to=to,
        reply_to=reply_to)

    msg.attach_alternative(html_message, 'text/html')

    return msg.send()


def price_list_approved(price_list):
    details_link = absolute_reverse('data_capture:price_list_details',
                                    kwargs={'id': price_list.pk})

    ctx = {
        'price_list': price_list,
        'details_link': details_link,
    }

    if price_list.status is not SubmittedPriceList.STATUS_APPROVED:
        raise AssertionError('price_list.status must be STATUS_APPROVED')

    result = send_mail(
        subject='CALC Price List Approved',
        template='data_capture/email/price_list_approved.html',
        ctx=ctx,
        reply_to=[settings.HELP_EMAIL],
        to=[price_list.submitter.email],
    )
    return EmailResult(
        was_successful=result is 1,
        context=ctx
    )


def price_list_retired(price_list):
    details_link = absolute_reverse('data_capture:price_list_details',
                                    kwargs={'id': price_list.pk})

    ctx = {
        'price_list': price_list,
        'details_link': details_link,
    }

    if price_list.status is not SubmittedPriceList.STATUS_RETIRED:
        raise AssertionError('price_list.status must be STATUS_RETIRED')

    result = send_mail(
        subject='CALC Price List Retired',
        template='data_capture/email/price_list_retired.html',
        ctx=ctx,
        reply_to=[settings.HELP_EMAIL],
        to=[price_list.submitter.email],
    )
    return EmailResult(
        was_successful=result is 1,
        context=ctx
    )


def price_list_rejected(price_list):
    details_link = absolute_reverse('data_capture:price_list_details',
                                    kwargs={'id': price_list.pk})

    ctx = {
        'price_list': price_list,
        'details_link': details_link,
    }

    result = send_mail(
        subject='CALC Price List Rejected',
        template='data_capture/email/price_list_rejected.html',
        ctx=ctx,
        reply_to=[settings.HELP_EMAIL],
        to=[price_list.submitter.email]
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
        subject='CALC Region 10 bulk data results - upload #{}'.format(
            upload_source.id),
        template='data_capture/email/bulk_upload_succeeded.html',
        ctx=ctx,
        reply_to=[settings.HELP_EMAIL],
        to=[upload_source.submitter.email],
    )
    return EmailResult(
        was_successful=result is 1,
        context=ctx
    )


def bulk_upload_failed(upload_source, traceback):
    r10_upload_link = absolute_reverse(
        'data_capture:bulk_region_10_step_1')

    ctx = {
        'upload_source': upload_source,
        'traceback': traceback,
        'r10_upload_link': r10_upload_link
    }

    result = send_mail(
        subject='CALC Region 10 bulk data results - upload #{}'.format(
            upload_source.id
        ),
        template='data_capture/email/bulk_upload_failed.html',
        ctx=ctx,
        reply_to=[settings.HELP_EMAIL],
        to=[upload_source.submitter.email],
    )
    return EmailResult(
        was_successful=result is 1,
        context=ctx
    )


def approval_reminder(count_unreviewed):
    unreviewed_url = absolute_reverse(
        'admin:data_capture_unreviewedpricelist_changelist')

    ctx = {
        'unreviewed_url': unreviewed_url,
    }

    superusers = User.objects.filter(is_superuser=True)
    recipients = [s.email for s in superusers if s.email]

    result = send_mail(
        subject='CALC Reminder - {} price list{} not reviewed'.format(
            count_unreviewed, pluralize(count_unreviewed)),
        template='data_capture/email/approval_reminder.html',
        ctx=ctx,
        reply_to=[settings.HELP_EMAIL],
        to=recipients,
    )
    return EmailResult(
        was_successful=result is 1,  # or count of superusers
        context=ctx
    )
