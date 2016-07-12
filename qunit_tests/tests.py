import os
import subprocess

from django.core import management
from django.test import LiveServerTestCase

# This file was taken from https://github.com/jonkemp/qunit-phantomjs-runner.
RUNNER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'vendor', 'runner.js')


class QunitTests(LiveServerTestCase):
    def test_qunit(self):
        subprocess.check_call([
            'phantomjs', RUNNER_PATH, self.live_server_url + '/tests/'
        ])

    @classmethod
    def setUpClass(cls):
        management.call_command('collectstatic', '--noinput', '--link',
                                verbosity=0)
        super(QunitTests, cls).setUpClass()
