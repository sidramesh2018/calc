from django.test import TestCase
from django.core.management import call_command

from contracts.mommy_recipes import get_contract_recipe


class Tests(TestCase):
    def setUp(self):
        get_contract_recipe().make(_quantity=10)

    def test_data_quality_report_command_does_not_explode(self):
        call_command('data_quality_report')

    def test_data_quality_report_view_does_not_explode(self):
        res = self.client.get('/data-quality-report/')
        self.assertEqual(res.status_code, 200)
