from django.test import TestCase, override_settings
from django.contrib.auth.models import User

from .schedules.fake_schedule import FakeSchedulePriceList
from .schedules import registry


@override_settings(
    # This will make tests run faster.
    PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'],
    # Ignore our custom auth backend so we can log the user in via
    # Django 1.8's login helpers.
    AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'],
    DATA_CAPTURE_SCHEDULES=[
        'data_capture.schedules.fake_schedule.FakeSchedulePriceList',
    ],
)
class StepTestCase(TestCase):
    def login(self):
        user = User.objects.create_user(username='foo', password='bar')
        assert self.client.login(username='foo', password='bar')
        return user

    def set_fake_gleaned_data(self, rows):
        session = self.client.session
        pricelist = FakeSchedulePriceList(rows)
        session['data_capture:schedule'] = registry.get_classname(pricelist)
        session['data_capture:gleaned_data'] = registry.serialize(pricelist)
        session.save()

    def setUp(self):
        registry._init()

    def assertRedirectsToLogin(self, url):
        res = self.client.get(url)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(
            res['Location'],
            'http://testserver/auth/login?next=%s' % url
        )


class Step1Tests(StepTestCase):
    url = '/data-capture/step/1'

    def test_login_is_required(self):
        self.assertRedirectsToLogin(self.url)

    def test_get_is_ok(self):
        self.login()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)


class Step2Tests(StepTestCase):
    url = '/data-capture/step/2'

    def test_login_is_required(self):
        self.assertRedirectsToLogin(self.url)

    def test_gleaned_data_is_required(self):
        self.login()
        res = self.client.get(self.url)
        self.assertRedirects(res, Step1Tests.url)


class Step3Tests(StepTestCase):
    url = '/data-capture/step/3'

    def test_login_is_required(self):
        self.assertRedirectsToLogin(self.url)

    def test_gleaned_data_is_required(self):
        self.login()
        res = self.client.get(self.url)
        self.assertRedirects(res, Step1Tests.url)

    def test_gleaned_data_with_valid_rows_is_required(self):
        self.login()
        self.set_fake_gleaned_data([])
        res = self.client.get(self.url)
        self.assertRedirects(res, Step2Tests.url)


class Step4Tests(StepTestCase):
    url = '/data-capture/step/4'

    def test_get_is_ok(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)
