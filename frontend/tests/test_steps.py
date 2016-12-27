from django.test import SimpleTestCase

from frontend.steps import StepsWidget


class StepsWidgetTests(SimpleTestCase):
    def test_it_works(self):
        steps = StepsWidget(
            labels=('foo', 'bar', 'baz'),
            current=2
        )
        html = str(steps)
        assert 'bar' in html
        assert 'Step 2 of 3' in html
