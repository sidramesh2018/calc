import io

from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth.models import Group

from ..management.commands import initgroups


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

    def test_creates_expected_groups(self):
        output = io.StringIO()
        call_command('initgroups', stdout=output)
        for role in initgroups.ROLES:
            self.assertIsNotNone(Group.objects.get(name=role))
