from django.test import SimpleTestCase

from frontend.steps import StepsWidget, Step


class StepsWidgetTests(SimpleTestCase):
    def test_context_works(self):
        steps = StepsWidget(
            labels=('foo', 'bar', 'baz'),
            current=2
        )
        ctx = steps.build_context()
        self.assertEqual(ctx['steps'], [
            Step('foo', 1, False),
            Step('bar', 2, True),
            Step('baz', 3, False),
        ])
        self.assertEqual(ctx['current_step'], ctx['steps'][1])

    def test_rendering_works(self):
        steps = StepsWidget(
            labels=('foo', 'bar', 'baz'),
            current=2
        )
        html = steps()
        assert 'bar' in html
        assert 'Step 2 of 3' in html
