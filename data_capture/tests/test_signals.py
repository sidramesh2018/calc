from functools import wraps
from unittest.mock import patch
from .test_models import ModelTestCase


class MockLogger():
    def __init__(self):
        self.logs = []

    def info(self, fmt, *args):
        self.logs.append(fmt % args)


def mock_logged(fn):
    @wraps(fn)
    @patch('data_capture.signals.logger', MockLogger())
    def wrapper(self):
        import data_capture.signals
        return fn(self, data_capture.signals.logger)

    return wrapper


class PriceListTests(ModelTestCase):
    @mock_logged
    def test_creating_submitted_price_list_logs_message(self, logger):
        self.create_price_list().save()
        self.assertEqual(logger.logs, [
            'Creating SubmittedPriceList for GS-123-4567, submitted by foo.'
        ])

    @mock_logged
    def test_updating_submitted_price_list_does_not_log_message(self, logger):
        pl = self.create_price_list()
        pl.save()
        self.assertEqual(len(logger.logs), 1)
        pl.retire(pl.submitter)
        self.assertEqual(len(logger.logs), 1)
