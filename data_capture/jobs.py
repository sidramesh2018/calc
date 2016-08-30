import logging
import traceback
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import transaction
from django.template.loader import render_to_string
from django_rq import job

from .r10_spreadsheet_converter import Region10SpreadsheetConverter
from contracts.loaders.region_10 import Region10Loader
from contracts.models import Contract, BulkUploadContractSource


contracts_logger = logging.getLogger('contracts')


@transaction.atomic
def _process_bulk_upload(upload_source):
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


@job
def process_bulk_upload_and_send_email(upload_source_id):
    contracts_logger.info(
        "Starting bulk upload processing (pk=%d)." % upload_source_id
    )
    upload_source = BulkUploadContractSource.objects.get(
        pk=upload_source_id
    )
    ctx = {'upload_source': upload_source}
    successful = False
    try:
        num_contracts, num_bad_rows = _process_bulk_upload(upload_source)
        ctx['num_contracts'] = num_contracts
        ctx['num_bad_rows'] = num_bad_rows
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
    return ctx
