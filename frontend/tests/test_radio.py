from django.test import SimpleTestCase

from .. import radio


class RadioTests(SimpleTestCase):
    def test_it_raises_error_when_id_is_not_present(self):
        rad = radio.UswdsRadioSelect(choices=[('1', 'foo')])
        with self.assertRaisesRegexp(
            ValueError,
            'USWDS-style radios must have "id" attributes'
        ):
            rad.render('my-radios', '1')

    def test_it_renders(self):
        rad = radio.UswdsRadioSelect(
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
