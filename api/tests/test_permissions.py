from unittest import mock
from django.test import SimpleTestCase, override_settings

from ..permissions import WhiteListPermission


@override_settings(REST_FRAMEWORK={'WHITELIST': ['1.1.2.2']})
class WhiteListPermissionTests(SimpleTestCase):
    @override_settings(REST_FRAMEWORK={'WHITELIST': None})
    def test_it_returns_true_when_no_whitelist_setting(self):
        w = WhiteListPermission()
        self.assertTrue(w.has_permission(None, None))

    def test_it_returns_true_when_forwarded_for_ip_is_whitelisted(self):
        w = WhiteListPermission()
        req = mock.MagicMock(
            META={'HTTP_X_FORWARDED_FOR': '5.5.5.5, 1.1.2.2, 2.2.3.3'}
        )
        self.assertTrue(w.has_permission(req, None))
        req = mock.MagicMock(
            META={'HTTP_X_FORWARDED_FOR': '  1.1.2.2  '}
        )
        self.assertTrue(w.has_permission(req, None))

    def test_it_returns_false_when_forwarded_for_ip_is_not_whitelisted(self):
        w = WhiteListPermission()
        req = mock.MagicMock(
            META={'HTTP_X_FORWARDED_FOR': '5.5.5.5, 2.2.3.3'}
        )
        self.assertFalse(w.has_permission(req, None))

    def test_it_returns_true_when_remote_addr_is_whitelisted(self):
        w = WhiteListPermission()
        req = mock.MagicMock(
            META={'REMOTE_ADDR': '1.1.2.2'}
        )
        self.assertTrue(w.has_permission(req, None))

    def test_it_returns_false_when_remote_addr_is_not_whitelisted(self):
        w = WhiteListPermission()
        req = mock.MagicMock(
            META={'REMOTE_ADDR': '5.6.7.8'}
        )
        self.assertFalse(w.has_permission(req, None))

    def test_it_returns_false_when_neither_header_has_whitelisted_ip(self):
        w = WhiteListPermission()
        req = mock.MagicMock(
            META={
                'HTTP_X_FORWARDED_FOR': '5.5.5.5, 2.2.3.3',
                'REMOTE_ADDR': '5.6.7.8'
            }
        )
        self.assertFalse(w.has_permission(req, None))

    def test_it_prefers_forwarded_for_to_remote_addr(self):
        w = WhiteListPermission()
        req = mock.MagicMock(
            META={
                'HTTP_X_FORWARDED_FOR': '5.5.5.5, 2.2.3.3',
                'REMOTE_ADDR': '1.1.2.2'
            }
        )
        self.assertFalse(w.has_permission(req, None))
