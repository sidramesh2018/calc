from textwrap import dedent

from django import template
from django.utils.safestring import SafeString


register = template.Library()


@register.tag
def example(parser, token):
    '''
    An an HTML code snippet example to a style guide.
    '''

    nodelist = parser.parse(('endexample',))
    parser.delete_first_token()
    return ExampleNode(nodelist)


class ExampleNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        html = SafeString(dedent(self.nodelist.render(context)).strip())

        t = context.template.engine.get_template('styleguide_example.html')

        return t.render(template.Context({'html': html}))
