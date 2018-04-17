from pathlib import Path
from django.utils.safestring import SafeString
from django.shortcuts import render
from django.urls import reverse


MY_DIR = Path(__file__).parent.resolve()

EXAMPLES_DIR = MY_DIR / 'templates' / 'styleguide_fullpage_examples'

REGEX = r'([0-9A-Za-z_\-]+)'


def get_html_source(name):
    filename = EXAMPLES_DIR / f'{name}.html'
    return SafeString(filename.read_text())


def get_url(name):
    return reverse('styleguide:fullpage_example', args=(name,))


def view(request, name):
    html = get_html_source(name)
    return render(request, 'styleguide_fullpage_example.html', {
        'html': html,
    })
