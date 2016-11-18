import io
import django.contrib.auth
from django.conf.urls import url
from django.test import override_settings
from django.http import HttpResponse
from django.core.management import call_command

from hourglass.urls import urlpatterns
from hourglass.tests.common import BaseLoginTestCase
from data_capture.tests.common import FAKE_SCHEDULE
from data_capture.schedules import registry
from frontend.tests.test_selenium import SeleniumTestCase
from frontend import safe_mode


USERNAME = 'boop'
PASSWORD = 'passwordy'


def autologin(request):
    user = django.contrib.auth.authenticate(
        username=USERNAME,
        password=PASSWORD
    )
    if user is None:
        raise Exception('Unable to authenticate')
    django.contrib.auth.login(request, user)
    request.session[safe_mode.SESSION_KEY] = True
    return HttpResponse('{} is now logged in'.format(
        user.email
    ))


urlpatterns += [
    url(r'^autologin/$', autologin),
]


@override_settings(
    ROOT_URLCONF=__name__,
    DATA_CAPTURE_SCHEDULES=[FAKE_SCHEDULE],
    # This will make tests run faster.
    PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'],
    # Ignore our custom auth backend so we can log the user in via
    # Django 1.8's login helpers.
    AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'],
)
class DataCaptureTests(SeleniumTestCase):
    screenshot_filename = 'data_capture.png'

    def test_data_capture(self):
        registry._init()
        call_command('initgroups', stdout=io.StringIO())
        t = BaseLoginTestCase()
        t.create_user(
            username=USERNAME,
            password=PASSWORD,
            email='boop.jones@gsa.gov',
            groups=('Data Administrators',)
        )
        self.load('/autologin')
        self.load('/data-capture/step/1')

        self.driver.find_element_by_name('contract_number')\
            .send_keys('GS-123-4567')
        e = self.driver.find_element_by_name('vendor_name')
        e.send_keys('Battaglia Sausage Peddlers, Inc.')
        e.submit()

        self.driver.find_element_by_css_selector(
            '[for="id_is_small_business_0"]'
        ).click()

        self.driver.find_element_by_css_selector(
            '[for="id_contractor_site_2"]'
        ).click()

        self.driver.find_element_by_name('contract_start_1').send_keys('04')
        self.driver.find_element_by_name('contract_start_2').send_keys('28')
        self.driver.find_element_by_name('contract_start_0').send_keys('2016')

        self.driver.find_element_by_name('contract_end_1').send_keys('03')
        self.driver.find_element_by_name('contract_end_2').send_keys('27')
        e = self.driver.find_element_by_name('contract_end_0')
        e.send_keys('2017')
        e.submit()
