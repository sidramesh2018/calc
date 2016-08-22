from django import forms


class UploadWidget(forms.widgets.FileInput):
    '''
    This widget represents an upload widget that the user can
    easily drag-and-drop files into.

    It is tightly coupled to upload.js.
    '''

    def __init__(self, attrs=None, degraded=False, required=True,
                 accept=(".xlsx", ".xls", ".csv"),
                 extra_instructions='XLS, XLSX, or CSV format, please.'):
        super().__init__(attrs=attrs)
        self.required = required
        self.degraded = degraded
        self.accept = accept
        self.extra_instructions = extra_instructions

    def render(self, name, value, attrs=None):
        degraded_str = ' data-force-degradation' if self.degraded else ''
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

        return "\n".join([
            '<upload-widget%s>' % degraded_str,
            '  %s' % super().render(name, value, final_attrs),
            '  <div class="upload-chooser">',
            '    <label for="%s">Choose file</label>' % id_for_label,
            '    <span>%s</span>' % self.extra_instructions,
            '  </div>',
            '</upload-widget>'
        ])
