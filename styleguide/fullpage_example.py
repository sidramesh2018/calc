from pathlib import Path
from django.utils.safestring import SafeString
from django.shortcuts import render
from django.urls import reverse
from django.http import Http404


MY_DIR = Path(__file__).parent.resolve()

EXAMPLES_DIR = MY_DIR / 'templates' / 'styleguide_fullpage_examples'

REGEX = r'([0-9A-Za-z_\-]+)'


def to_path(name):
    return EXAMPLES_DIR / f'{name}.html'


def get_html_source(name):
    return SafeString(to_path(name).read_text())


def get_url(name):
    return reverse('styleguide:fullpage_example', args=(name,))


def exists(name):
    return to_path(name).exists()


def view(request, name):
    if not exists(name):
        raise Http404("fullpage example does not exist")
    html = get_html_source(name)
    return render(request, 'styleguide_fullpage_example.html', {
        'html': html,
    })
