from django.test import TestCase

from styleguide import email_examples


class StyleguideTests(TestCase):

    def test_styleguide_returns_200(self):
        response = self.client.get('/styleguide/')
        self.assertEqual(response.status_code, 200)

    def test_styleguide_ajaxform_returns_200(self):
        response = self.client.get('/styleguide/ajaxform')
        self.assertEqual(response.status_code, 200)

    def test_styleguide_date_returns_200(self):
        response = self.client.get('/styleguide/date')
        self.assertEqual(response.status_code, 200)

    def test_styleguide_radio_checkbox_returns_200(self):
        response = self.client.get('/styleguide/radio-checkbox')
        self.assertEqual(response.status_code, 200)

    def test_styleguide_email_examples_return_200(self):
        for example in email_examples.examples:
            html_response = self.client.get(example.html_url)
            self.assertEqual(html_response.status_code, 200)

            plaintext_response = self.client.get(example.plaintext_url)
            self.assertEqual(plaintext_response.status_code, 200)
