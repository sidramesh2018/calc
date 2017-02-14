from unittest import mock
from django.test import TestCase


class DataExplorerTests(TestCase):
    def test_logout_works(self):
        with mock.patch('django.contrib.auth.logout') as logout_mock:
            response = self.client.get('/logout/')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(logout_mock.call_count, 1)
            self.assertEqual(response.status_code, 200)
