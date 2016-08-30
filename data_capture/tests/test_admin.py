from unittest.mock import patch
from django.contrib import messages
from django.test import override_settings

from .. import admin, models
from .common import FAKE_SCHEDULE
from .test_models import ModelTestCase


@override_settings(
    DATA_CAPTURE_SCHEDULES=[FAKE_SCHEDULE],
)
class AdminTestCase(ModelTestCase):
    def setUp(self):
        super().setUp()
        self.price_list = self.create_price_list()
        self.price_list.save()
        self.row = self.create_row(price_list=self.price_list)
        self.row.save()

    def setup_user(self):
        self.user = self.login(is_superuser=True)


@override_settings(
    # Strangely, disabling DEBUG mode silences some errors in Django
    # admin views, so we'll enforce it so that any errors are raised.
    DEBUG=True,
)
class ViewTests(AdminTestCase):
    def test_submittedpricelistrow_list_returns_200(self):
        res = self.client.get('/admin/data_capture/submittedpricelistrow/')
        self.assertEqual(res.status_code, 200)

    def test_submittedpricelist_list_returns_200(self):
        res = self.client.get('/admin/data_capture/submittedpricelist/')
        self.assertEqual(res.status_code, 200)

    def test_unapproved_submittedpricelist_detail_returns_200(self):
        res = self.client.get(
            '/admin/data_capture/submittedpricelist/{}/'.format(
                self.price_list.id
            )
        )
        self.assertEqual(res.status_code, 200)

    def test_approved_submittedpricelist_detail_returns_200(self):
        self.price_list.approve()
        res = self.client.get(
            '/admin/data_capture/submittedpricelist/{}/'.format(
                self.price_list.id
            )
        )
        self.assertEqual(res.status_code, 200)


@patch.object(messages, 'add_message')
class ActionTests(AdminTestCase):
    def test_approve_ignores_approved_price_lists(self, mock):
        self.price_list.approve()
        admin.approve(None, "fake request",
                      models.SubmittedPriceList.objects.all())
        mock.assert_called_once_with(
            "fake request",
            messages.INFO,
            '0 price list(s) have been approved and added to CALC.'
        )

    def test_unapprove_ignores_unapproved_price_lists(self, mock):
        admin.unapprove(None, "fake request",
                        models.SubmittedPriceList.objects.all())
        mock.assert_called_once_with(
            "fake request",
            messages.INFO,
            '0 price list(s) have been unapproved and removed from CALC.'
        )

    def test_approve_works(self, mock):
        admin.approve(None, "fake request",
                      models.SubmittedPriceList.objects.all())
        mock.assert_called_once_with(
            "fake request",
            messages.INFO,
            '1 price list(s) have been approved and added to CALC.'
        )
        self.price_list.refresh_from_db()
        self.assertTrue(self.price_list.is_approved)

    def test_unapprove_works(self, mock):
        self.price_list.approve()
        admin.unapprove(None, "fake request",
                        models.SubmittedPriceList.objects.all())
        mock.assert_called_once_with(
            "fake request",
            messages.INFO,
            '1 price list(s) have been unapproved and removed from CALC.'
        )
        self.price_list.refresh_from_db()
        self.assertFalse(self.price_list.is_approved)
