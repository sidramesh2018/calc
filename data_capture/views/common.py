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
    def __init__(self, template_format, view_format, globs):
        self._template_format = template_format
        self._view_format = view_format
        self._globs = globs
        self._num_steps = None

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

    @property
    def num_steps(self):
        if self._num_steps is None:
            for i in range(1, 999):
                if self._view_format.format(i) not in self._globs:
                    self._num_steps = i - 1
                    break
        return self._num_steps
