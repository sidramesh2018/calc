import logging
from django.dispatch import receiver
from django.db.models.signals import pre_save


from .models import SubmittedPriceList


logger = logging.getLogger('calc')


@receiver(pre_save, sender=SubmittedPriceList)
def log_price_list_creation(sender, instance=None, **kwargs):
    if instance is not None and instance.pk is None:
        logger.info(
            f'Creating SubmittedPriceList for {instance.contract_number}, '
            f'submitted by {instance.submitter}.'
        )
