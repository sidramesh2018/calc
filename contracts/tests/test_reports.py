from django.test import TestCase
from django.core.management import call_command

from contracts.mommy_recipes import get_contract_recipe


class Tests(TestCase):
    def test_data_quality_report_does_not_explode(self):
        get_contract_recipe().make(_quantity=100)
        call_command('data_quality_report')
