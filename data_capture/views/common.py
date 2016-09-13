from functools import wraps
from django.conf.urls import url
from django.contrib import messages
from django.shortcuts import render
from django.template.defaultfilters import pluralize


def add_generic_form_error(request, form):
    messages.add_message(
        request, messages.ERROR,
        'Oops, please correct the error{} below and try again.'
            .format(pluralize(form.errors))
    )


class Steps:
    def __init__(self, template_format):
        self.template_format = template_format
        self._views = []

    def step(self, func):
        step_number = self.num_steps + 1

        if not func.__name__.endswith(str(step_number)):
            raise ValueError('Expected {} to end with the number {}'.format(
                func.__name__,
                self.num_steps
            ))

        @wraps(func)
        def wrapper(*args, **kwargs):
            kwargs['step'] = StepRenderer(self, step_number)
            return func(*args, **kwargs)

        self._views.append(wrapper)
        return wrapper

    @property
    def urls(self):
        urlpatterns = []

        for i in range(self.num_steps):
            view = self._views[i]
            regex = r'^' + str(i + 1) + r'$'
            urlpatterns.append(url(regex, view, name=view.__name__))

        return urlpatterns

    @property
    def num_steps(self):
        return len(self._views)


class StepRenderer:
    def __init__(self, steps, step_number):
        self.steps = steps
        self.number = step_number

    def context(self, context=None):
        final_ctx = {'step': self}
        if context:
            final_ctx.update(context)
        return final_ctx

    def template_name(self):
        return self.steps.template_format.format(self.number)

    def render(self, request, context=None):
        return render(request, self.template_name(),
                      self.context(context))

    def description(self):
        return "Step {} of {}".format(
            self.number,
            self.steps.num_steps
        )
