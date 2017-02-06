import re

from .util import CfTestCase


class CloudFrontTests(CfTestCase):
    def test_app_is_fronted_by_cloudfront(self):
        res = self.client.get('/blarg')
        self.assertIn('X-Amz-Cf-Id', res.headers)

    def test_form_submission_works(self):
        '''
        Mitigation against https://github.com/18F/calc/issues/1198.
        '''

        self.browser.open('/styleguide/radio-checkbox')
        self.browser.session.headers['Referer'] = self.ORIGIN
        form = self.browser.get_form()
        form['radios'].value = '2'
        form['checkboxes'].value = 'a'
        self.browser.submit_form(form)
        self.assertEqual(self.browser.response.status_code, 200)
        self.assertIn('You chose radio option #2!',
                      self.browser.response.content.decode('utf-8'))

    def test_api_supports_cors(self):
        '''
        Mitigation against https://github.com/18F/calc/issues/1307.
        '''

        res = self.client.get('/')
        m = re.search(r'var API_HOST = "([^"]+)"',
                      res.content.decode('utf-8'))
        api_url = m.group(1)

        res = self.client.get(
            api_url + 'search/?format=json&q=zzzzzzzz&query_type=match_all',
            headers={'Origin': self.ORIGIN}
        )

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), [])
        self.assertEqual(res.headers['Access-Control-Allow-Origin'], '*')
