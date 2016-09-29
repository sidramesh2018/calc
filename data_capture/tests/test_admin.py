import io
import unittest.mock as mock
from django.conf import settings
from django.core.management import call_command
from django.contrib import messages
from django.contrib.auth.models import User
from django.test import override_settings, TestCase

from .. import admin, models, email
from .common import FAKE_SCHEDULE
from .test_models import ModelTestCase


@override_settings(
    DATA_CAPTURE_SCHEDULES=[FAKE_SCHEDULE],
)
class AdminTestCase(ModelTestCase):
    def setUp(self):
        super().setUp()
        self.price_list = self.create_price_list()
        self.price_list.save()
        self.row = self.create_row(price_list=self.price_list)
        self.row.save()

    def setup_user(self):
        call_command('initgroups', stdout=io.StringIO())
        self.user = self.login(
            is_staff=True,
            groups=('Data Administrators',)
        )


@override_settings(
    # Strangely, disabling DEBUG mode silences some errors in Django
    # admin views, so we'll enforce it so that any errors are raised.
    DEBUG=True,
    # And enabling DEBUG will enable the Django Debug Toolbar, which
    # unfortunately massively slows down our tests, so let's disable that.
    INSTALLED_APPS=tuple([
        name for name in settings.INSTALLED_APPS
        if name != 'debug_toolbar'
    ]),
    MIDDLEWARE_CLASSES=tuple([
        name for name in settings.MIDDLEWARE_CLASSES
        if name != 'hourglass.middleware.DebugOnlyDebugToolbarMiddleware'
    ]),
)
class DebugAdminTestCase(AdminTestCase):
    pass


class CustomUserCreationFormTests(TestCase):
    def test_checks_uniqueness_of_email(self):
        User.objects.create_user(username='blerg', email='foo@gsa.gov')
        form = admin.CustomUserCreationForm({'email': 'foo@gsa.gov'})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'email': ['That email address is already in use.']
        })

    def test_generate_username_works(self):
        form = admin.CustomUserCreationForm()
        self.assertEqual(form.generate_username('boop.jones@gsa.gov'),
                         'boopjones')

    def test_generate_username_appends_number_when_needed(self):
        User.objects.create_user(username='boopjones')
        form = admin.CustomUserCreationForm()
        self.assertEqual(form.generate_username('boop.jones@gsa.gov'),
                         'boopjones1')

    def test_generate_username_raises_exception_when_attempts_maxed_out(self):
        User.objects.create_user(username='boopjones')
        User.objects.create_user(username='boopjones1')
        form = admin.CustomUserCreationForm()
        with self.assertRaisesRegexp(
            Exception,
            'unable to generate username for '
            'boop.jones@gsa.gov after 2 attempts'
        ):
            form.generate_username('boop.jones@gsa.gov', max_attempts=2)

    def test_save_sets_username(self):
        form = admin.CustomUserCreationForm({'email': 'foo@gsa.gov'})
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.username, 'foo')
        self.assertEqual(user.email, 'foo@gsa.gov')


class SuperuserViewTests(DebugAdminTestCase):
    def setup_user(self):
        self.user = self.login(is_superuser=True)

    def test_can_set_superuser(self):
        res = self.client.get('/admin/auth/user/{}/'.format(self.user.id))
        self.assertContains(res, 'Superuser')
        self.assertEqual(res.status_code, 200)

    def test_can_see_superusers(self):
        self.create_user(username='superdawg', is_superuser=True)
        res = self.client.get('/admin/auth/user/')
        self.assertContains(res, 'superdawg')
        self.assertEqual(res.status_code, 200)


class NonSuperuserViewTests(DebugAdminTestCase):
    def test_user_add_returns_200(self):
        res = self.client.get('/admin/auth/user/add/')
        self.assertContains(res, 'First, enter an email address',
                            status_code=200)

    def test_cannot_set_superuser(self):
        res = self.client.get('/admin/auth/user/{}/'.format(self.user.id))
        self.assertNotContains(res, 'Superuser')
        self.assertEqual(res.status_code, 200)

    def test_cannot_see_superusers(self):
        self.create_user(username='superdawg', is_superuser=True)
        res = self.client.get('/admin/auth/user/')
        self.assertNotContains(res, 'superdawg')
        self.assertEqual(res.status_code, 200)

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


@mock.patch.object(messages, 'add_message')
class ActionTests(AdminTestCase):
    def test_approve_ignores_approved_price_lists(self, mock):
        self.price_list.approve()
        admin.approve(None, "fake request",
                      models.SubmittedPriceList.objects.all())
        mock.assert_called_once_with(
            "fake request",
            messages.INFO,
            '0 price list(s) have been approved and added to CALC.'
        )

    def test_unapprove_ignores_unapproved_price_lists(self, mock):
        admin.unapprove(None, "fake request",
                        models.SubmittedPriceList.objects.all())
        mock.assert_called_once_with(
            "fake request",
            messages.INFO,
            '0 price list(s) have been unapproved and removed from CALC.'
        )

    def test_approve_works(self, msg_mock):
        with mock.patch.object(email, 'price_list_approved',
                               wraps=email.price_list_approved) as em_monkey:
            admin.approve(None, "fake request",
                          models.SubmittedPriceList.objects.all())
            msg_mock.assert_called_once_with(
                "fake request",
                messages.INFO,
                '1 price list(s) have been approved and added to CALC.'
            )
            em_monkey.assert_called_once_with(self.price_list)

        self.price_list.refresh_from_db()
        self.assertTrue(self.price_list.is_approved)

    def test_unapprove_works(self, msg_mock):
        with mock.patch.object(email, 'price_list_unapproved',
                               wraps=email.price_list_unapproved) as em_monkey:
            self.price_list.approve()
            admin.unapprove(None, "fake request",
                            models.SubmittedPriceList.objects.all())
            msg_mock.assert_called_once_with(
                "fake request",
                messages.INFO,
                '1 price list(s) have been unapproved and removed from CALC.'
            )
            em_monkey.assert_called_once_with(self.price_list)

        self.price_list.refresh_from_db()
        self.assertFalse(self.price_list.is_approved)
