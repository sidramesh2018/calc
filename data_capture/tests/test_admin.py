from django.test import override_settings

from .common import FAKE_SCHEDULE
from .test_models import ModelTestCase


@override_settings(
    DATA_CAPTURE_SCHEDULES=[FAKE_SCHEDULE],
    # Strangely, disabling DEBUG mode silences some errors in Django
    # admin views, so we'll enforce it so that any errors are raised.
    DEBUG=True
)
class AdminTests(ModelTestCase):
    def setUp(self):
        super().setUp()
        self.price_list = self.create_price_list()
        self.price_list.save()
        self.row = self.create_row(price_list=self.price_list)
        self.row.save()

    def setup_user(self):
        self.user = self.login(is_superuser=True)

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
