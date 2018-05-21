from django.test import TestCase
from django.core.management import call_command

from contracts.mommy_recipes import get_contract_recipe


class Tests(TestCase):
    def setUp(self):
        get_contract_recipe().make(_quantity=10)
        get_contract_recipe().make(
            labor_category='senior outlier',
            min_years_experience=1,
            education_level='HS',
            current_price=999999
        )

    def test_data_quality_report_command_does_not_explode(self):
        call_command('data_quality_report')

    def test_data_quality_report_view_does_not_explode(self):
        res = self.client.get('/data-quality-report/')
        self.assertEqual(res.status_code, 200)

    def test_data_quality_report_detail_view_does_not_explode(self):
        res = self.client.get('/data-quality-report/outliers/')
        self.assertContains(res, 'senior outlier')

    def test_invalid_data_quality_report_detail_returns_404(self):
        res = self.client.get('/data-quality-report/boooooooop/')
        self.assertEqual(res.status_code, 404)
