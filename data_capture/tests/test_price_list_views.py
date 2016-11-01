import json

from model_mommy import mommy
from django.test import override_settings
from django.utils import timezone

from hourglass.tests.common import ProtectedViewTestCase
from ..models import SubmittedPriceList
from ..management.commands.initgroups import PRICE_LIST_UPLOAD_PERMISSION
from .common import FAKE_SCHEDULE, uploaded_csv_file
from ..schedules import registry


class ListViewTests(ProtectedViewTestCase):
    url = '/data-capture/price-lists'

    def login(self, **kwargs):
        kwargs['permissions'] = [PRICE_LIST_UPLOAD_PERMISSION]
        return super().login(**kwargs)

    def test_get_is_ok(self):
        self.login()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_has_context_vars(self):
        self.login()
        res = self.client.get(self.url)
        ctx = res.context
        self.assertIn('approved_price_lists', ctx)
        self.assertIn('new_price_lists', ctx)
        self.assertIn('rejected_price_lists', ctx)
        self.assertIn('unapproved_price_lists', ctx)

    def test_only_includes_price_lists_for_user(self):
        user = self.login()
        other_user = self.create_user('other_user')

        for val, label in SubmittedPriceList.STATUS_CHOICES:
            mommy.make(SubmittedPriceList,
                       submitter=user,
                       status=val)

            mommy.make(SubmittedPriceList,
                       submitter=other_user,
                       status=val)

        res = self.client.get(self.url)
        ctx = res.context
        self.assertEqual(len(ctx['approved_price_lists']), 1)
        self.assertEqual(len(ctx['new_price_lists']), 1)
        self.assertEqual(len(ctx['rejected_price_lists']), 1)
        self.assertEqual(len(ctx['unapproved_price_lists']), 1)


@override_settings(DATA_CAPTURE_SCHEDULES=[FAKE_SCHEDULE])
class DetailsViewTests(ProtectedViewTestCase):
    url = '/data-capture/price-lists/'

    def login(self, **kwargs):
        kwargs['permissions'] = [PRICE_LIST_UPLOAD_PERMISSION]
        return super().login(**kwargs)

    def setUp(self):
        super().setUp()
        a_user = self.create_user('a_user')
        p = registry.load_from_upload(FAKE_SCHEDULE, uploaded_csv_file())
        serialized = registry.serialize(p)
        self.price_list = mommy.make(SubmittedPriceList,
                                     submitter=a_user,
                                     contract_number="GS-12-1234",
                                     serialized_gleaned_data=json.dumps(
                                        serialized),
                                     created_at=timezone.now(),
                                     status=SubmittedPriceList.STATUS_NEW)
        self.url += str(self.price_list.pk)

    def test_get_is_ok(self):
        self.login()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_has_context_vars(self):
        self.login()
        res = self.client.get(self.url)
        ctx = res.context
        self.assertIn('price_list', ctx)
        self.assertIn('gleaned_data', ctx)
        self.assertEqual(ctx['price_list'], self.price_list)
