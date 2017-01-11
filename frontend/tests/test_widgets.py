from django.test import SimpleTestCase

from .. import widgets


class CheckboxTests(SimpleTestCase):
    def test_it_raises_error_when_id_is_not_present(self):
        chk = widgets.UswdsCheckbox(choices=[('1', 'foo')])
        with self.assertRaisesRegexp(
            ValueError,
            'USWDS-style inputs must have "id" attributes'
        ):
            chk.render('my-checkboxes', '1')

    def test_it_renders(self):
        chk = widgets.UswdsCheckbox(
            {'id': 'baz'},
            choices=[('1', 'foo'), ('2', 'bar')]
        )
        self.assertHTMLEqual(
            chk.render('my-checkboxes', '1'),
            ('<ul id="baz">'
             '  <li>'
             '    <input checked="checked" id="baz_0" name="my-checkboxes" '
             '     type="checkbox" value="1" />'
             '    <label for="baz_0">foo</label>'
             '  </li>'
             '  <li>'
             '    <input id="baz_1" name="my-checkboxes" type="checkbox" '
             '     value="2" />'
             '    <label for="baz_1">bar</label>'
             '  </li>'
             '</ul>')
        )


class RadioTests(SimpleTestCase):
    def test_it_raises_error_when_id_is_not_present(self):
        rad = widgets.UswdsRadioSelect(choices=[('1', 'foo')])
        with self.assertRaisesRegexp(
            ValueError,
            'USWDS-style inputs must have "id" attributes'
        ):
            rad.render('my-radios', '1')

    def test_it_renders(self):
        rad = widgets.UswdsRadioSelect(
            {'id': 'baz'},
            choices=[('1', 'foo'), ('2', 'bar')]
        )
        self.assertHTMLEqual(
            rad.render('my-radios', '1'),
            ('<ul id="baz">'
             '  <li>'
             '    <input checked="checked" id="baz_0" name="my-radios" '
             '     type="radio" value="1" />'
             '    <label for="baz_0">foo</label>'
             '  </li>'
             '  <li>'
             '    <input id="baz_1" name="my-radios" type="radio" '
             '     value="2" />'
             '    <label for="baz_1">bar</label>'
             '  </li>'
             '</ul>')
        )
