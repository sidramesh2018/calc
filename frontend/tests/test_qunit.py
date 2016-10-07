import os
import subprocess

from django.test import LiveServerTestCase, override_settings

from hourglass.urls import urlpatterns, tests_url
from .utils import build_static_assets
from .test_selenium import WD_TESTING_BROWSER, SeleniumTestCase


urlpatterns += [tests_url]

TESTS_URL = '/tests/?hidepassed'

if WD_TESTING_BROWSER == 'phantomjs':
    RUNNER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               'vendor', 'runner.js')

    @override_settings(ROOT_URLCONF=__name__)
    class QunitTests(LiveServerTestCase):
        '''
        Run QUnit tests directly via phantomjs, bypassing Selenium to
        simplify the test process and reduce the chance of something
        weird exploding in our face.
        '''

        def test_qunit(self):
            subprocess.check_call([
                'phantomjs', RUNNER_PATH, self.live_server_url + TESTS_URL
            ])

        @classmethod
        def setUpClass(cls):
            build_static_assets()
            super(QunitTests, cls).setUpClass()
else:
    @override_settings(ROOT_URLCONF=__name__)
    class QunitTests(SeleniumTestCase):
        '''
        Run QUnit tests in a real-world browser via Selenium.
        '''

        def test_qunit(self):
            self.load(TESTS_URL)

            FAILED = '#qunit-testresult .failed'

            def are_results_loaded():
                els = self.driver.find_elements_by_css_selector(FAILED)

                return len(els) > 0

            self.wait_for(are_results_loaded)

            failed = self.driver.find_element_by_css_selector(FAILED).text

            if failed != '0':
                raise Exception("{} qunit test(s) failed".format(failed))
