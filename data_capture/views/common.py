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


class StepBuilder:
    def __init__(self, template_format):
        self._template_format = template_format
        self._views = []

    def context(self, step, context=None):
        final_ctx = {
            'step_number': step,
            'NUM_STEPS': self.num_steps
        }
        if context:
            final_ctx.update(context)
        return final_ctx

    def template_name(self, step):
        return self._template_format.format(step)

    def render(self, step, request, context=None):
        return render(request, self.template_name(step),
                      self.context(step, context))

    def step(self, func):
        self._views.append(func)
        if not func.__name__.endswith(str(self.num_steps)):
            raise ValueError('Expected {} to end with the number {}'.format(
                func.__name__,
                self.num_steps
            ))
        return func

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
