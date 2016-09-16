from django.test import TestCase


class SafeModeTests(TestCase):
    def test_enable_works(self):
        res = self.client.post('/safe-mode/enable')
        self.assertTrue(self.client.session['enable_safe_mode'])
        self.assertRedirects(res, '/')

    def test_disable_works(self):
        res = self.client.post('/safe-mode/disable')
        self.assertFalse(self.client.session['enable_safe_mode'])
        self.assertRedirects(res, '/')

    def test_endpoints_redirect_to_referrer_if_present(self):
        for path in ['/safe-mode/enable', '/safe-mode/disable']:
            res = self.client.post(path, HTTP_REFERER='/foo')
            self.assertRedirects(res, '/foo', fetch_redirect_response=False)
