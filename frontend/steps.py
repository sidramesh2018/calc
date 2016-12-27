from collections import namedtuple

from django.template.loader import render_to_string


Step = namedtuple('Step', ['label', 'number', 'current'])


class StepsWidget:
    '''
    The steps widget can be used to visualize the user's progress through a
    multi-step process.

    While it is described as a "widget", it is not actually a widget
    in the Django sense--i.e., it is not used to present users with
    a form UI.
    '''

    def __init__(self, labels, current):
        self.labels = labels
        self.current = current

    def render(self):
        steps = [
            Step(label=label, number=i, current=(i == self.current))
            for label, i in zip(self.labels, range(1, len(self.labels) + 1))
        ]
        return render_to_string('frontend/steps.html', {
            'current_step': steps[self.current - 1],
            'steps': steps,
        })

    def __str__(self):
        return self.render()
