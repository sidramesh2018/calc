import json

from ..forms.price_list import Step2Form
from ..models import SubmittedPriceList
from ..schedules.fake_schedule import FakeSchedulePriceList
from ..schedules import registry
from .common import StepTestCase, FAKE_SCHEDULE, FAKE_SCHEDULE_EXAMPLE_PATH


class PriceListStepTestCase(StepTestCase):
    # TODO: Move individual setUp functions here if applicable
    def set_fake_gleaned_data(self, rows):
        session = self.client.session
        pricelist = FakeSchedulePriceList(rows)
        session['data_capture']['schedule'] = registry.get_classname(pricelist)
        session['data_capture']['gleaned_data'] = registry.serialize(pricelist)
        session.save()

    def setUp(self):
        registry._init()


class Step1Tests(PriceListStepTestCase):
    url = '/data-capture/step/1'

    valid_form = {
        'schedule': FAKE_SCHEDULE,
        'contract_number': 'GS-123-4567',
        'vendor_name': 'foo'
    }

    def test_login_is_required(self):
        self.assertRedirectsToLogin(self.url)

    def test_get_is_ok(self):
        self.login()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_valid_post_sets_session_data(self):
        self.login()
        self.client.post(self.url, self.valid_form)
        self.assertEqual(self.client.session['data_capture']['schedule'],
             FAKE_SCHEDULE)
        self.assertEqual(self.client.session['data_capture']['contract_number'], 'GS-123-4567')
        self.assertEqual(self.client.session['data_capture']['vendor_name'], 'foo')

    def test_valid_post_redirects_to_step_2(self):
        self.login()
        res = self.client.post(self.url, self.valid_form)
        self.assertRedirects(res, Step2Tests.url)

    def test_invalid_post_returns_html(self):
        self.login()
        res = self.client.post(self.url, {})
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'This field is required')
        self.assertHasMessage(
            res,
            'error',
            'Oops, please correct the errors below and try again.'
        )


class Step2Tests(PriceListStepTestCase):
    url = '/data-capture/step/2'

    # TODO: Add contract start/end and year
    valid_form = {
        'contractor_site': 'Customer',
        'is_small_business': False
    }

    def setUp(self):
        session = self.client.session
        session['data_capture'] = {
            'schedule': FAKE_SCHEDULE,
            'contract_number': 'GS-123-4567',
            'vendor_name': 'foo'
        }
        session.save()

    def test_login_is_required(self):
        self.assertRedirectsToLogin(self.url)

    def test_get_is_ok(self):
        self.login()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_valid_post_creates_models(self):
        user = self.login()
        self.client.post(self.url, self.valid_form)
        p = SubmittedPriceList.objects.filter(
            contract_number='GS-123-4567'
        )[0]
        self.assertEqual(p.schedule, FAKE_SCHEDULE)
        self.assertEqual(p.vendor_name, 'foo')
        self.assertEqual(p.contractor_site, 'Customer')
        self.assertEqual(p.is_small_business, False)
        self.assertEqual(p.submitter, user)

    def test_valid_post_redirects_to_step_3(self):
        self.login()
        res = self.client.post(self.url, self.valid_form)
        self.assertRedirects(res, Step3Tests.url)

    def test_invalid_post_returns_html(self):
        self.login()
        res = self.client.post(self.url, {})
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'This field is required')
        self.assertHasMessage(
            res,
            'error',
            'Oops, please correct the errors below and try again.'
        )


class Step3Tests(PriceListStepTestCase):
    url = '/data-capture/step/3'
    csvpath = FAKE_SCHEDULE_EXAMPLE_PATH
    rows = [{
        'education': 'Bachelors',
        'price': '15.00',
        'service': 'Project Manager',
        'sin': '132-40',
        'years_experience': '7'
    }]

    def setUp(self):
        session = self.client.session
        session['data_capture'] = {
            'schedule': FAKE_SCHEDULE,
            'contract_number': 'GS-123-4567',
            'vendor_name': 'foo'
        }
        session.save()

    def ajax_post(self, data):
        res = self.client.post(self.url, data,
                               HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(res.status_code, 200)
        return res, json.loads(res.content.decode('utf-8'))

    def test_login_is_required(self):
        self.assertRedirectsToLogin(self.url)

    def test_get_is_ok(self):
        self.login()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_valid_post_updates_session_data(self):
        self.login()
        with open(self.csvpath) as f:
            self.client.post(self.url, {
                'file': f
            })
            self.assertEqual(self.client.session['data_capture']['schedule'],
                 FAKE_SCHEDULE)
            gleaned_data = self.client.session['data_capture']['gleaned_data']
            gleaned_data = registry.deserialize(gleaned_data)
            assert isinstance(gleaned_data, FakeSchedulePriceList)
            self.assertEqual(gleaned_data.rows, [{
                'education': 'Bachelors',
                'price': '15.00',
                'service': 'Project Manager',
                'sin': '132-40',
                'years_experience': '7'
            }])

    def test_valid_post_via_xhr_returns_json(self):
        self.login()
        with open(self.csvpath) as f:
            res, json_data = self.ajax_post({
                'file': f
            })
            self.assertEqual(json_data, {
                'redirect_url': '/data-capture/step/4'
            })

    def test_valid_post_redirects_to_step_4(self):
        self.login()
        with open(self.csvpath) as f:
            res = self.client.post(self.url, {
                'file': f
            })
            self.assertRedirects(res, Step4Tests.url)

class Step4Tests(PriceListStepTestCase):
    url = '/data-capture/step/4'
    rows = [{
        'education': 'Bachelors',
        'price': '15.00',
        'service': 'Project Manager',
        'sin': '132-40',
        'years_experience': '7'
    }, {
        'education': 'School of hard knocks',
        'price': '0',
        'service': 'Oil change & tune up',
        'sin': 'absolved',
        'years_experience': 'vii'
    }]

    def setUp(self):
        session = self.client.session
        # user = self.login()
        # print(user)
        session['data_capture'] = {
            'schedule': FAKE_SCHEDULE,
            'contract_number': 'GS-123-4567',
            'vendor_name': 'foo',
            'contractor_site': 'Customer',
            'is_small_business': False
        }
        # This doesn't work.
        # form = Step2Form({
            # 'contract_number': ['GS-123-4567'],
            # 'vendor_name': ['foo'],
            # 'schedule': [FAKE_SCHEDULE],
            # 'contractor_site': 'Customer',
            # 'is_small_business': 'False',
            # 'submitter_id': ['foo']
        # })
        # form.is_valid()
        # print(form.errors)
        # price_list = form.save()
        # session['price_list_id'] = price_list.id
        session.save()

    def test_login_is_required(self):
        self.assertRedirectsToLogin(self.url)

    def test_gleaned_data_is_required(self):
        self.login()
        res = self.client.get(self.url)
        self.assertRedirects(res, Step3Tests.url)

    def test_get_is_ok(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_gleaned_data_with_valid_rows_is_required(self):
        self.login()
        self.set_fake_gleaned_data([])
        res = self.client.get(self.url)
        self.assertRedirects(res, Step3Tests.url)

    # FAIL
    def test_valid_post_discards_invalid_rows(self):
        self.login()
        self.set_fake_gleaned_data(self.rows)
        print(self.client)
        self.client.post(self.url, self.client.session['data_capture'])
        # p = SubmittedPriceList.objects.get(id=self.client.session['price_list_id'])

        # gleaned_data = registry.deserialize(
            # json.loads(p.serialized_gleaned_data)
        # )
        # assert isinstance(gleaned_data, FakeSchedulePriceList)
        self.assertLess(gleaned_data.valid_rows.count, self.rows.count)

    # FAIL
    def test_valid_post_redirects_to_step_5(self):
        self.login()
        # model posting stuff here when it works
        self.assertEqual(res.status_code, 200)

    # FAIL
    def test_invalid_post_raises_error(self):
        self.login()
        self.set_fake_gleaned_data([])
        res = self.client.post(self.url, self.set_fake_gleaned_data([]))
        self.assertHasMessage(
            res,
            'error',
            'What error message should this be?'
        )

class Step5Tests(StepTestCase):
    url = '/data-capture/step/5'

    def test_get_is_ok(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_login_is_required(self):
        self.assertRedirectsToLogin(self.url)

    def test_gleaned_data_is_required(self):
        self.login()
        res = self.client.get(self.url)
        self.assertRedirects(res, Step3Tests.url)

    def test_session_is_deleted(self):
        self.login()
        self.set_fake_gleaned_data(self.rows)
        self.set_vendor_info(self.vendor_info)
        self.client.post(self.url, self.valid_form)
        assert 'data_capture' not in self.client.session
