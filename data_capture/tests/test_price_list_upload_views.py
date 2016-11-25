import json
from datetime import datetime

from ..models import SubmittedPriceList
from ..schedules.fake_schedule import FakeSchedulePriceList
from ..schedules import registry
from ..management.commands.initgroups import PRICE_LIST_UPLOAD_PERMISSION
from .common import (StepTestCase, FAKE_SCHEDULE, uploaded_csv_file,
                     create_csv_content)


class HandleCancelMixin():
    def test_cancel_clears_session_and_redirects(self):
        self.login()
        res = self.client.post(self.url, {'cancel': ''})
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res['Location'], 'http://testserver/')
        session = self.client.session
        for k in list(session.keys()):
            self.assertFalse(k.startswith('data_capture:'))


class RequireGleanedDataMixin():
    def test_gleaned_data_is_required(self):
        self.login()
        session = self.client.session
        session['data_capture:price_list'] = self.session_data
        session.save()
        res = self.client.get(self.url)
        self.assertRedirects(res, Step3Tests.url)


class PriceListStepTestCase(StepTestCase):
    # TODO: Move individual setUp functions here if applicable
    def set_fake_gleaned_data(self, rows):
        session = self.client.session
        pricelist = FakeSchedulePriceList(rows)
        session['data_capture:price_list']['schedule'] = \
            registry.get_classname(pricelist)
        session['data_capture:price_list']['gleaned_data'] = \
            registry.serialize(pricelist)
        session.save()

    def delete_price_list_from_session(self):
        session = self.client.session
        del session['data_capture:price_list']
        session.save()

    def setUp(self):
        super().setUp()
        registry._init()

    def login(self, **kwargs):
        kwargs['permissions'] = [PRICE_LIST_UPLOAD_PERMISSION]
        return super().login(**kwargs)


class Step1Tests(PriceListStepTestCase):
    url = '/data-capture/step/1'

    valid_form = {
        'schedule': FAKE_SCHEDULE,
        'contract_number': 'GS-123-4567',
        'vendor_name': 'foo'
    }

    def test_get_is_ok(self):
        self.login()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_valid_post_sets_session_data(self):
        self.login()
        self.client.post(self.url, self.valid_form)
        session_pl = self.client.session['data_capture:price_list']
        session_data = session_pl['step_1_POST']
        self.assertEqual(session_data['schedule'], FAKE_SCHEDULE)
        self.assertEqual(session_data['contract_number'], 'GS-123-4567')
        self.assertEqual(session_data['vendor_name'], 'foo')

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
            'Oops! Please correct the following errors.'
        )


class Step2Tests(PriceListStepTestCase, HandleCancelMixin):
    url = '/data-capture/step/2'

    valid_form = {
        'contractor_site': 'Customer',
        'is_small_business': 'False',
        'contract_start_0': '1985',
        'contract_start_1': '07',
        'contract_start_2': '08',
        'contract_end_0': '1989',
        'contract_end_1': '04',
        'contract_end_2': '14'
    }

    def setUp(self):
        super().setUp()
        session = self.client.session
        session['data_capture:price_list'] = {
            'step_1_POST': Step1Tests.valid_form,
        }
        session.save()

    def test_get_is_ok(self):
        self.login()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_going_back_to_previous_step_prefills_its_form(self):
        self.login()
        res = self.client.get(Step1Tests.url)
        self.assertEqual(res.context['form'].data, Step1Tests.valid_form)

    def test_redirects_to_step_1_if_not_completed(self):
        self.login()
        self.delete_price_list_from_session()
        res = self.client.get(self.url)
        self.assertRedirects(res, Step1Tests.url)

    def test_valid_post_updates_session_data(self):
        self.login()
        self.client.post(self.url, self.valid_form)
        session_pl = self.client.session['data_capture:price_list']
        posted_data = session_pl['step_2_POST']
        self.assertEqual(posted_data['contractor_site'],
                         self.valid_form['contractor_site'])
        self.assertEqual(posted_data['is_small_business'],
                         self.valid_form['is_small_business'])

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
            'Oops! Please correct the following errors.'
        )


class Step3Tests(PriceListStepTestCase, HandleCancelMixin):
    url = '/data-capture/step/3'

    rows = [{
        'education': 'Bachelors',
        'price': '15.00',
        'service': 'Project Manager',
        'sin': '132-40',
        'years_experience': '7'
    }]

    def setUp(self):
        super().setUp()
        session = self.client.session
        session['data_capture:price_list'] = {
            'step_1_POST': Step1Tests.valid_form,
            'step_2_POST': Step2Tests.valid_form,
        }
        session.save()

    def ajax_post(self, data):
        res = self.client.post(self.url, data,
                               HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(res.status_code, 200)
        return res, json.loads(res.content.decode('utf-8'))

    def test_get_is_ok(self):
        self.login()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_going_back_to_previous_step_prefills_its_form(self):
        self.login()
        res = self.client.get(Step2Tests.url)
        self.assertEqual(res.context['form'].data, Step2Tests.valid_form)

    def test_redirects_to_step_2_if_not_completed(self):
        self.login()
        self.delete_price_list_from_session()
        res = self.client.get(self.url)
        self.assertRedirects(res, Step2Tests.url, target_status_code=302)

    def test_redirects_if_gleaned_data_in_session_with_valid_rows(self):
        self.login()
        self.set_fake_gleaned_data(self.rows)
        res = self.client.get(self.url)
        self.assertRedirects(res, Step3DataTests.url)

    def test_doesnt_redirect_if_force_param_is_on(self):
        self.login()
        self.set_fake_gleaned_data(self.rows)
        res = self.client.get(self.url+'?force=on')
        self.assertEqual(res.status_code, 200)

    def test_redirects_if_force_param_is_not_on(self):
        self.login()
        self.set_fake_gleaned_data(self.rows)
        res = self.client.get(self.url+'?force=whatever')
        self.assertRedirects(res, Step3DataTests.url)

    def test_valid_post_updates_session_data(self):
        self.login()
        self.client.post(self.url, {
            'file': uploaded_csv_file()
        })
        session_pl = self.client.session['data_capture:price_list']
        self.assertEqual(session_pl['step_1_POST']['schedule'],
                         FAKE_SCHEDULE)
        gleaned_data = session_pl['gleaned_data']
        gleaned_data = registry.deserialize(gleaned_data)
        assert isinstance(gleaned_data, FakeSchedulePriceList)
        self.assertEqual(gleaned_data.rows, [{
            'education': 'Bachelors',
            'price': '15.00',
            'service': 'Project Manager',
            'sin': '132-40',
            'years_experience': '7'
        }])

    def test_post_with_gleaned_data_and_uploaded_file_checks_validity(self):
        self.login()
        self.set_fake_gleaned_data(self.rows)
        res = self.client.post(self.url, {
            'file': uploaded_csv_file(
                content=create_csv_content(rows=[
                    ['132-40', 'Project Manager', 'invalid edu', '7', '15.00']
                ]))
        })
        self.assertRedirects(res, Step3ErrorTests.url)

    def test_valid_post_via_xhr_returns_json(self):
        self.login()
        res, json_data = self.ajax_post({
            'file': uploaded_csv_file()
        })
        self.assertEqual(json_data, {
            'redirect_url': Step4Tests.url
        })

    def test_post_with_invalid_rows_via_xhr_returns_json_redirect(self):
        self.login()
        res, json_data = self.ajax_post({
            'file': uploaded_csv_file(
                content=create_csv_content(rows=[
                    ['132-40', 'Project Manager', 'invalid edu', '7', '15.00']
                ]))
        })
        self.assertEqual(json_data, {
            'redirect_url': Step3ErrorTests.url
        })

    def test_valid_post_redirects_to_step_4(self):
        self.login()
        res = self.client.post(self.url, {
            'file': uploaded_csv_file()
        })
        self.assertRedirects(res, Step4Tests.url)

    def test_post_with_invalid_rows_redirects_to_step_3_errors(self):
        self.login()
        res = self.client.post(self.url, {
            'file': uploaded_csv_file(
                content=create_csv_content(rows=[
                    ['132-40', 'Project Manager', 'invalid edu', '7', '15.00']
                ]))
        })
        self.assertRedirects(res, Step3ErrorTests.url)

    def test_invalid_post_returns_html(self):
        self.login()
        res = self.client.post(self.url, {})
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, r'<!DOCTYPE html>')
        self.assertContains(res, r'This field is required')
        self.assertHasMessage(
            res,
            'error',
            'Oops! Please correct the following error.'
        )

    def test_invalid_post_via_xhr_returns_json(self):
        self.login()
        res, json_data = self.ajax_post({})
        assert '<!DOCTYPE html>' not in json_data['form_html']
        self.assertRegexpMatches(json_data['form_html'],
                                 r'This field is required')
        self.assertHasMessage(
           res,
           'error',
           'Oops! Please correct the following error.'
        )


class Step3DataTests(PriceListStepTestCase,
                     RequireGleanedDataMixin,
                     HandleCancelMixin):
    url = '/data-capture/step/3/data'

    session_data = {
        'step_1_POST': Step1Tests.valid_form,
        'step_2_POST': Step2Tests.valid_form,
    }

    rows = [{
        'education': 'Bachelors',
        'price': '15.00',
        'service': 'Project Manager',
        'sin': '132-40',
        'years_experience': '7'
    }]

    session_data = {
        'step_1_POST': Step1Tests.valid_form,
        'step_2_POST': Step2Tests.valid_form,
    }

    def setUp(self):
        super().setUp()
        session = self.client.session
        session['data_capture:price_list'] = self.session_data
        session.save()

    def test_redirects_if_no_gleaned_data(self):
        self.login()
        res = self.client.get(self.url)
        self.assertRedirects(res, Step3Tests.url)

    def test_redirects_if_no_valid_rows(self):
        self.login()
        self.set_fake_gleaned_data([])
        res = self.client.get(self.url)
        self.assertRedirects(res, Step3Tests.url)

    def test_get_is_ok(self):
        self.login()
        self.set_fake_gleaned_data(self.rows)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)
        self.assertIn('gleaned_data', res.context)


class Step3ErrorTests(PriceListStepTestCase,
                      RequireGleanedDataMixin,
                      HandleCancelMixin):
    url = '/data-capture/step/3/errors'

    rows = [{
        'education': 'Bachelors',
        'price': '15.00',
        'service': 'Project Manager',
        'sin': '132-40',
        'years_experience': '7'
    }]

    session_data = {
        'step_1_POST': Step1Tests.valid_form,
        'step_2_POST': Step2Tests.valid_form,
    }

    def setUp(self):
        super().setUp()
        session = self.client.session
        session['data_capture:price_list'] = self.session_data
        session.save()

    def test_get_is_ok(self):
        self.login()
        self.set_fake_gleaned_data(self.rows)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)


class Step4Tests(PriceListStepTestCase,
                 HandleCancelMixin, RequireGleanedDataMixin):
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
    session_data = {
        'step_1_POST': Step1Tests.valid_form,
        'step_2_POST': Step2Tests.valid_form,
    }

    valid_post_data = {}
    valid_post_data.update(Step1Tests.valid_form)
    valid_post_data.update(Step2Tests.valid_form)

    def test_get_is_ok(self):
        self.login()
        session = self.client.session
        session['data_capture:price_list'] = self.session_data
        session.save()
        self.set_fake_gleaned_data(self.rows)
        res = self.client.get(self.url)
        self.assertFalse(res.context['show_edit_form'])
        self.assertEqual(res.status_code, 200)

    def test_context_has_prev_url_if_query_param_present(self):
        self.login()
        session = self.client.session
        session['data_capture:price_list'] = self.session_data
        session.save()
        self.set_fake_gleaned_data(self.rows)
        res = self.client.get(self.url + '?prev={}'.format(Step3DataTests.url))
        self.assertEqual(res.status_code, 200)
        self.assertIn('prev_url', res.context)
        self.assertEqual(res.context['prev_url'], '/data-capture/step/3/data')

    def test_prev_url_is_none_if_query_param_not_safe(self):
        self.login()
        session = self.client.session
        session['data_capture:price_list'] = self.session_data
        session.save()
        self.set_fake_gleaned_data(self.rows)
        res = self.client.get(self.url + '?prev={}'.format('http://foo.com'))
        self.assertEqual(res.status_code, 200)
        self.assertIn('prev_url', res.context)
        self.assertEqual(res.context['prev_url'], None)

    def test_redirects_if_no_gleaned_data(self):
        self.login()
        session = self.client.session
        session['data_capture:price_list'] = self.session_data
        session.save()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res['Location'], 'http://testserver' + Step3Tests.url)

    def test_redirects_if_no_valid_rows_in_gleaned_data(self):
        self.login()
        session = self.client.session
        session['data_capture:price_list'] = self.session_data
        session.save()
        self.set_fake_gleaned_data([])
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res['Location'], 'http://testserver' + Step3Tests.url)

    def test_gleaned_data_with_valid_rows_is_required_on_POST(self):
        self.login()
        session = self.client.session
        session['data_capture:price_list'] = self.session_data
        session.save()
        self.set_fake_gleaned_data([])
        res = self.client.post(self.url)
        self.assertEqual(res.status_code, 400)

    def test_saving_changes_saves_and_redirects_back_to_self(self):
        self.login()
        session = self.client.session
        session['data_capture:price_list'] = self.session_data
        session.save()
        self.set_fake_gleaned_data(self.rows)
        data = self.valid_post_data.copy()
        data['vendor_name'] = 'changed in step 4!'
        data['contractor_site'] = 'Both'
        data['save-changes'] = ''
        res = self.client.post(self.url, data)
        session_pl = self.client.session['data_capture:price_list']
        step_1_data = session_pl['step_1_POST']
        self.assertEqual(step_1_data['schedule'], FAKE_SCHEDULE)
        self.assertEqual(step_1_data['contract_number'], 'GS-123-4567')
        self.assertEqual(step_1_data['vendor_name'], 'changed in step 4!')
        step_2_data = session_pl['step_2_POST']
        self.assertEqual(step_2_data['contractor_site'], 'Both')
        self.assertEqual(SubmittedPriceList.objects.all().count(), 0)
        self.assertRedirects(res, Step4Tests.url)

    def test_invalid_post_shows_errors(self):
        self.login()
        session = self.client.session
        session['data_capture:price_list'] = self.session_data
        session.save()
        self.set_fake_gleaned_data(self.rows)
        data = self.valid_post_data.copy()
        data['contractor_site'] = 'LOL'
        res = self.client.post(self.url, data)
        self.assertTrue(res.context['show_edit_form'])
        self.assertContains(res, 'LOL is not one of the available choices')

    def test_valid_post_creates_models(self):
        user = self.login()
        session = self.client.session
        session['data_capture:price_list'] = self.session_data
        session.save()
        self.set_fake_gleaned_data(self.rows)
        self.client.post(self.url, self.valid_post_data)
        p = SubmittedPriceList.objects.filter(
            contract_number='GS-123-4567'
        )[0]
        self.assertEqual(p.schedule, FAKE_SCHEDULE)
        self.assertEqual(p.vendor_name, 'foo')
        self.assertEqual(p.contractor_site, 'Customer')
        self.assertEqual(p.is_small_business, False)
        self.assertEqual(p.submitter, user)
        self.assertEqual(p.status_changed_by, user)
        self.assertEqual(p.status, SubmittedPriceList.STATUS_NEW)
        self.assertEqual(p.status_changed_at.date(), datetime.now().date())

    def test_valid_post_clears_session_and_redirects_to_step_5(self):
        self.login()
        session = self.client.session
        session['data_capture:price_list'] = self.session_data
        session.save()
        self.set_fake_gleaned_data(self.rows)
        res = self.client.post(self.url, self.valid_post_data)
        assert 'data_capture:price_list' not in self.client.session
        self.assertRedirects(res, Step5Tests.url)


class Step5Tests(PriceListStepTestCase):
    url = '/data-capture/step/5'

    def test_get_is_ok(self):
        self.login()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)
