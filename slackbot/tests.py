from unittest.mock import patch
from django.test import TestCase

from . import signals
from data_capture.models import SubmittedPriceList


class SignalsTests(TestCase):
    @patch.object(signals, 'sendmsg')
    def test_msg_sent_on_submittedpricelist_creation(self, m):
        instance = SubmittedPriceList()
        instance.id = 5
        instance.status = SubmittedPriceList.STATUS_UNREVIEWED
        signals.on_submittedpricelist_save(
            SubmittedPriceList,
            created=True,
            instance=instance,
        )
        m.assert_called_with(
            'A new <http://example.com/admin/data_capture/'
            'unreviewedpricelist/5/change/|price list> has been submitted!'
        )
