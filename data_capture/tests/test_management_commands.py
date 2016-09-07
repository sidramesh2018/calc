import io

from django.test import TestCase
from django.core.management import call_command


class TestInitgroups(TestCase):
    def test_it_creates_group_iff_it_does_not_exist(self):
        output = io.StringIO()
        call_command('initgroups', stdout=output)
        self.assertRegex(output.getvalue(),
                         'Group does not exist, creating it.')

        output = io.StringIO()
        call_command('initgroups', stdout=output)
        self.assertNotRegex(output.getvalue(),
                            'Group does not exist, creating it.')
