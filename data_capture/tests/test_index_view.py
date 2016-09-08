from .common import StepTestCase
from data_explorer.templatetags.schedules import get_schedules


class IndexViewTestCase(StepTestCase):
    def test_schedule_filters_contain_SIN(self):
        response = self.client.get('')
        for schedule in get_schedules():
            matcher = '{SIN} - {name}'.format(**schedule)
            self.assertContains(response, matcher)
