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
        self.steps = [
            Step(label=label, number=i, current=(i == current))
            for label, i in zip(labels, range(1, len(labels) + 1))
        ]
        self.current_step = self.steps[current - 1]
        for step in self.steps:
            if not step.label:
                raise ValueError('Step {} has no label'.format(
                    step.number
                ))

    def render(self):
        return render_to_string('frontend/steps.html', self.__dict__)

    def __call__(self):
        '''
        A convenience for rendering the widget directly from a Django
        template.
        '''

        return self.render()

    def __repr__(self):
        return '<{} for step {} of {}: {}>'.format(
            self.__class__.__name__,
            self.current_step.number,
            len(self.steps),
            self.current_step.label
        )
