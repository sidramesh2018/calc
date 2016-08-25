import logging
import threading
import traceback
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import transaction

from .. import forms
from ..r10_spreadsheet_converter import Region10SpreadsheetConverter
from .common import add_generic_form_error
from frontend import ajaxform
from contracts.loaders.region_10 import Region10Loader
from contracts.models import Contract, BulkUploadContractSource


contracts_logger = logging.getLogger('contracts')


@user_passes_test(lambda u: u.is_staff)
def region_10_step_1(request):
    '''
    Start of Region 10 Bulk Upload - Upload the spreadsheet
    '''
    if request.method == 'GET':
        form = forms.Region10BulkUploadForm()
    elif request.method == 'POST':
        form = forms.Region10BulkUploadForm(request.POST, request.FILES)

        if form.is_valid():
            file = form.cleaned_data['file']

            upload_source = BulkUploadContractSource.objects.create(
                submitter=request.user,
                procurement_center=BulkUploadContractSource.REGION_10,
                has_been_loaded=False,
                original_file=file.read()
            )

            request.session['data_capture:upload_source_id'] = upload_source.pk

            return ajaxform.redirect(
                request,
                'data_capture:bulk_region_10_step_2'
            )
        else:
            add_generic_form_error(request, form)

    return ajaxform.render(
        request,
        context={
            'step_number': 1,
            'form': form,
        },
        template_name='data_capture/bulk_upload/region_10_step_1.html',
        ajax_template_name='data_capture/bulk_upload/'
                           'region_10_step_1_form.html',
    )


@user_passes_test(lambda u: u.is_staff)
def region_10_step_2(request):
    '''
    Confirm that the new data should be loaded

    TODO: Should we use a Form to have POST submit and  POST cancel
    instead of a simple link to step_3?
    '''
    upload_source_id = request.session.get('data_capture:upload_source_id')
    if upload_source_id is None:
        return redirect('data_capture:bulk_region_10_step_1')

    # Get the BulkUploadContractSource based on upload_source_id
    upload_source = BulkUploadContractSource.objects.get(pk=upload_source_id)

    file = ContentFile(upload_source.original_file)

    file_metadata = Region10SpreadsheetConverter(file).get_metadata()

    return render(request, 'data_capture/bulk_upload/region_10_step_2.html', {
        'step_number': 2,
        'file_metadata': file_metadata,
    })


@transaction.atomic
def process_bulk_upload(upload_source):
    file = ContentFile(upload_source.original_file)
    converter = Region10SpreadsheetConverter(file)

    contracts_logger.info("Deleting contract objects related to region 10.")

    # Delete existing contracts identified by the same
    # procurement_center
    Contract.objects.filter(
        upload_source__procurement_center=BulkUploadContractSource.REGION_10
    ).delete()

    contracts = []
    bad_rows = []

    contracts_logger.info("Generating new contract objects.")

    for row in converter.convert_next():
        try:
            c = Region10Loader.make_contract(row, upload_source=upload_source)
            contracts.append(c)
        except (ValueError, ValidationError) as e:
            bad_rows.append(row)

    contracts_logger.info("Saving new contract objects.")

    # Save new contracts
    Contract.objects.bulk_create(contracts)

    contracts_logger.info("Updating full-text search indexes.")

    # Update search field on Contract models
    Contract._fts_manager.update_search_field()

    # Update the upload_source
    upload_source.has_been_loaded = True
    upload_source.save()

    return len(contracts), len(bad_rows)


def process_bulk_upload_in_separate_thread(upload_source_id):
    def run():
        contracts_logger.info(
            "Starting bulk upload processing (pk=%d)." % upload_source_id
        )
        upload_source = BulkUploadContractSource.objects.get(
            pk=upload_source_id
        )
        ctx = {'upload_source': upload_source}
        successful = False
        try:
            num_contracts, num_bad_rows = process_bulk_upload(upload_source)
            ctx['num_contracts'] = num_contracts
            ctx['num_bad_rows'] = num_bad_rows
            kablooey
            successful = True
        except:
            contracts_logger.exception(
                'An exception occurred during bulk upload processing '
                '(pk=%d).' % upload_source_id
            )
            ctx['traceback'] = traceback.format_exc()
        ctx['successful'] = successful
        send_mail(
            subject='CALC Region 10 bulk data results - upload #%d' % (
                upload_source.id,
            ),
            message=render_to_string(
                'data_capture/bulk_upload/region_10_email.txt',
                ctx
            ),
            from_email=None,
            recipient_list=[upload_source.submitter.email]
        )
        contracts_logger.info(
            "Ending bulk upload processing (pk=%d)." % upload_source_id
        )

    thread = threading.Thread(target=run)
    thread.start()


@user_passes_test(lambda u: u.is_staff)
def region_10_step_3(request):
    '''Load data and show success screen'''
    upload_source_id = request.session.get('data_capture:upload_source_id')
    if upload_source_id is None:
        return redirect('data_capture:bulk_region_10_step_1')

    process_bulk_upload_in_separate_thread(upload_source_id)

    # remove the upload_source_id from session
    del request.session['data_capture:upload_source_id']

    return render(request, 'data_capture/bulk_upload/region_10_step_3.html', {
        'step_number': 3,
    })
