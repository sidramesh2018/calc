from django import forms
from django.forms.utils import flatatt
from django.utils.html import escape


class UploadWidget(forms.widgets.FileInput):
    '''
    This widget represents an upload widget that the user can
    easily drag-and-drop files into.

    It is tightly coupled to upload.js.
    '''

    def __init__(self, attrs=None, degraded=False, required=True,
                 accept=(".xlsx", ".xls", ".csv"),
                 extra_instructions='XLS, XLSX, or CSV format, please.',
                 existing_filename=None):
        super().__init__(attrs=attrs)
        self.required = required
        self.degraded = degraded
        self.accept = accept
        self.extra_instructions = extra_instructions
        self.existing_filename = existing_filename

    def render(self, name, value, attrs=None):
        final_attrs = {}
        if attrs:
            final_attrs.update(attrs)

        if self.required:
            # TODO: Django 1.10 automatically adds this attribute as needed
            # based on the form field, so we should remove this once we
            # upgrade.
            final_attrs['required'] = ''

        final_attrs['accept'] = ",".join(self.accept)
        final_attrs['is'] = 'upload-input'

        id_for_label = final_attrs.get('id', '')
        instructions = [self.extra_instructions or '']

        widget_attrs = {}

        if self.degraded:
            widget_attrs['data-force-degradation'] = ''

        if self.existing_filename:
            if 'required' in final_attrs:
                raise AssertionError(
                    'Using an existing filename is incompatible with '
                    'the "required" attribute'
                )
            widget_attrs['data-fake-initial-filename'] = self.existing_filename
            instructions.append(
                'Leave this field blank to continue using '
                '<code>{}</code>.'.format(
                    escape(self.existing_filename)
                )
            )

        return "\n".join([
            '<upload-widget%s>' % flatatt(widget_attrs),
            '  %s' % super().render(name, value, final_attrs),
            '  <div class="upload-chooser">',
            '    <label for="%s">Choose file</label>' % id_for_label,
            '    <span>%s</span>' % ' '.join(instructions),
            '  </div>',
            '</upload-widget>'
        ])
