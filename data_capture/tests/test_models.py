from datetime import datetime, date
from decimal import Decimal

from freezegun import freeze_time
from django.test import override_settings
from django.utils import timezone
from django.forms import ValidationError

from hourglass.tests.common import BaseLoginTestCase
from contracts.models import Contract
from ..schedules import registry
from ..schedules.fake_schedule import FakeSchedulePriceList
from ..models import SubmittedPriceList, SubmittedPriceListRow
from .common import FAKE_SCHEDULE


frozen_datetime = datetime(2017, 1, 12, 9, 15, 20)


class ModelTestCase(BaseLoginTestCase):
    DEFAULT_SCHEDULE = FAKE_SCHEDULE

    def setUp(self):
        super().setUp()
        registry._init()
        self.setup_user()

    def setup_user(self):
        self.user = self.create_user(username='foo', email='foo@example.com')

    def create_price_list(self, **kwargs):
        final_kwargs = dict(
            submitter=self.user,
            is_small_business=False,
            contract_number='GS-123-4567',
            vendor_name='UltraCorp',
            schedule=self.DEFAULT_SCHEDULE,
            contract_start=date(2016, 9, 1),
            contract_end=date(2021, 9, 1),
            escalation_rate=0,
            status=SubmittedPriceList.STATUS_UNREVIEWED,
            status_changed_by=self.user,
            status_changed_at=timezone.now(),
        )
        final_kwargs.update(kwargs)
        return SubmittedPriceList(**final_kwargs)

    def create_row(self, **kwargs):
        final_kwargs = dict(
            labor_category='Project Manager',
            min_years_experience=5,
            base_year_rate=10,
        )
        final_kwargs.update(kwargs)
        return SubmittedPriceListRow(**final_kwargs)


@override_settings(DATA_CAPTURE_SCHEDULES=[FAKE_SCHEDULE])
class ModelsTests(ModelTestCase):
    def test_add_row_works(self):
        p = self.create_price_list()
        p.save()
        row = p.add_row(
            labor_category='Project Manager',
            min_years_experience=5,
            base_year_rate=10,
        )
        self.assertEqual(list(p.rows.all()), [row])
        self.assertEqual(row.labor_category, 'Project Manager')
        self.assertEqual(row.min_years_experience, 5)
        self.assertEqual(row.base_year_rate, 10)

    def test_get_schedule_title_works(self):
        p = self.create_price_list(schedule=FAKE_SCHEDULE)
        self.assertEqual(p.get_schedule_title(),
                         FakeSchedulePriceList.title)

    def test_get_business_size_string_works(self):
        p = self.create_price_list(is_small_business=False)
        self.assertEqual(p.get_business_size_string(), 'O')

        p.is_small_business = True
        self.assertEqual(p.get_business_size_string(), 'S')

    @freeze_time(frozen_datetime)
    def test_change_status_works(self):
        original_user = self.create_user(username='boop', email="boop@beep")
        p = self.create_price_list(
            status=SubmittedPriceList.STATUS_UNREVIEWED,
            status_changed_by=original_user)
        p._change_status(SubmittedPriceList.STATUS_APPROVED, self.user)
        self.assertEqual(p.status, SubmittedPriceList.STATUS_APPROVED)
        self.assertEqual(p.status_changed_by, self.user)
        self.assertEqual(
            p.status_changed_at,
            timezone.make_aware(frozen_datetime))

    @freeze_time(frozen_datetime)
    def test_approve_works(self):
        p = self.create_price_list(
            contract_number='GS-123-4568',
            schedule=FAKE_SCHEDULE,
            escalation_rate=1
        )
        p.save()
        row = self.create_row(labor_category='Software Engineer',
                              price_list=p)
        row.save()
        self.create_row(price_list=p, is_muted=True).save()
        p.approve(self.user)

        self.assertEqual(Contract.objects.all().count(), 1)
        self.assertEqual(p.status, SubmittedPriceList.STATUS_APPROVED)
        self.assertEqual(p.status_changed_by, self.user)
        self.assertEqual(p.status_changed_at,
                         timezone.make_aware(frozen_datetime))

        contract = p.rows.all()[0].contract_model
        self.assertEqual(contract.idv_piid, 'GS-123-4568')
        self.assertEqual(contract.labor_category, 'Software Engineer')
        self.assertEqual(contract.schedule, FakeSchedulePriceList.title)
        self.assertEqual(contract.labor_category, 'Software Engineer')
        self.assertEqual(contract.hourly_rate_year1, Decimal(10.00))
        self.assertAlmostEqual(
            contract.hourly_rate_year2, Decimal(10.10), places=2)
        self.assertAlmostEqual(
            contract.hourly_rate_year3, Decimal(10.20), places=2)
        self.assertAlmostEqual(
            contract.hourly_rate_year4, Decimal(10.30), places=2)
        self.assertAlmostEqual(
            contract.hourly_rate_year5, Decimal(10.41), places=2)
        self.assertEqual(contract.contract_year, 1)
        self.assertEqual(contract.current_price, 10.00)
        self.assertAlmostEqual(
            contract.next_year_price, Decimal(10.10), places=2)
        self.assertAlmostEqual(
            contract.second_year_price, Decimal(10.20), places=2)

    @freeze_time(frozen_datetime)
    def test_retire_works(self):
        p = self.create_price_list()
        p.save()
        self.create_row(price_list=p).save()
        self.create_row(price_list=p, is_muted=True).save()
        p.approve(self.user)
        p.retire(self.user)
        self.assertEqual(p.status, SubmittedPriceList.STATUS_RETIRED)
        self.assertEqual(p.status_changed_by, self.user)
        self.assertEqual(p.status_changed_at,
                         timezone.make_aware(frozen_datetime))
        self.assertEqual(p.rows.all()[0].contract_model, None)
        self.assertEqual(Contract.objects.all().count(), 0)

    @freeze_time(frozen_datetime)
    def test_reject_works(self):
        p = self.create_price_list()
        p.save()
        self.create_row(price_list=p).save()
        p.reject(self.user)
        self.assertEqual(p.status, SubmittedPriceList.STATUS_REJECTED)
        self.assertEqual(p.status_changed_by, self.user)
        self.assertEqual(p.status_changed_at,
                         timezone.make_aware(frozen_datetime))
        self.assertEqual(p.rows.all()[0].contract_model, None)
        self.assertEqual(Contract.objects.all().count(), 0)

    def test_reject_raises_when_not_STATUS_UNREVIEWED(self):
        p = self.create_price_list()
        p.save()
        self.create_row(price_list=p).save()
        p.approve(self.user)
        with self.assertRaises(AssertionError):
            p.reject(self.user)

    @freeze_time(frozen_datetime)
    def test_unreview_works(self):
        p = self.create_price_list()
        p.save()
        self.create_row(price_list=p).save()
        p.approve(self.user)
        p.unreview(self.user)
        self.assertEqual(p.status, SubmittedPriceList.STATUS_UNREVIEWED)
        self.assertEqual(p.status_changed_by, self.user)
        self.assertEqual(p.status_changed_at,
                         timezone.make_aware(frozen_datetime))
        self.assertEqual(p.rows.all()[0].contract_model, None)
        self.assertEqual(Contract.objects.all().count(), 0)

    def test_row_stringify_works(self):
        self.assertEqual(str(self.create_row()), 'Submitted price list row')

    def test_get_latest_by_contract_number_works(self):
        p1 = self.create_price_list()
        p1.save()

        p2 = self.create_price_list()
        p2.save()

        latest = SubmittedPriceList.get_latest_by_contract_number(
            'GS-123-4567')
        self.assertEqual(p2, latest)

    def test_get_latest_by_contract_number_ignores_case(self):
        p = self.create_price_list(contract_number='GS-AA-bbbb')
        p.save()
        latest = SubmittedPriceList.get_latest_by_contract_number(
            'gs-AA-bbBB')
        self.assertEqual(p, latest)

    def test_contract_number_is_validated(self):
        p = self.create_price_list(contract_number='***GS-123-3456')
        with self.assertRaises(ValidationError) as cm:
            p.full_clean()
            self.assertIn('Please use only letters, numbers, and dashes (-).',
                          cm.exception)
