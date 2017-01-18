import re
import datetime
import pathlib
from django.shortcuts import render
from django.utils.safestring import mark_safe
import markdown


PATH = pathlib.Path(__file__).resolve().parent.parent / 'CHANGELOG.md'

ENCODING = 'utf-8'

RELEASE_HEADER_RE = re.compile(
    r'^## \[?([0-9.]+)[ \]]?',
    re.MULTILINE
    )

UNRELEASED_LINK_RE = re.compile(
    r'^\[unreleased\]: (.+\.\.\.HEAD)$',
    re.MULTILINE
    )

UNRELEASED_HEADER = '## [Unreleased][unreleased]'


def django_view(request):
    contents = strip_preamble(get_contents())
    html = mark_safe(markdown.markdown(contents))  # nosec
    return render(request, 'changelog.html', dict(html=html))


def get_contents():
    '''
    Return the contents of CHANGELOG.md.
    '''

    with PATH.open('r', encoding=ENCODING) as f:
        return f.read()


def get_unreleased_link(contents):
    '''
    Returns the URL that the "Unreleased" section is hyperlinked to, e.g.:

        >>> get_unreleased_link('[unreleased]: http://compare/v1.0.0...HEAD')
        'http://compare/v1.0.0...HEAD'
    '''

    return UNRELEASED_LINK_RE.search(contents).group(1)


def get_latest_release(contents):
    '''
    Return the latest release of the given changelog, e.g.:

        >>> get_latest_release('## 1.2.3 - 2017-01-01')
        '1.2.3'
    '''

    return RELEASE_HEADER_RE.search(contents).group(1)


def strip_preamble(contents):
    '''
    Removes any expository text before the beginning of the
    "Unreleased" section, if it's non-empty.  If the "Unreleased" section
    is empty, it is removed as well.
    '''

    if get_unreleased_notes(contents).strip():
        result = contents[contents.index(UNRELEASED_HEADER):]
    else:
        result = contents[RELEASE_HEADER_RE.search(contents).start():]
    return result


def bump_version(contents, new_version, date=None):
    '''
    Move the "Unreleased" section of the given changelog to a new release
    with the given version number.

    The new release will be hyperlinked to a GitHub diff between it and the
    previous release, while the "Unreleased" section will be emptied and
    hyperlinked to a GitHub diff between the new release and HEAD.

    Return the contents of the new changelog.
    '''

    if date is None:
        date = datetime.date.today()

    unreleased_diff_link = get_unreleased_link(contents)
    old_version = get_latest_release(contents)
    new_version_header = '## [{}][] - {}'.format(new_version, date)
    new_unreleased_diff_link = unreleased_diff_link.replace(
        'v' + old_version,
        'v' + new_version
        )
    new_version_diff_link = '[{}]: {}'.format(
        new_version,
        unreleased_diff_link.replace('HEAD', 'v' + new_version)
        )

    contents = contents.replace(
        UNRELEASED_HEADER,
        UNRELEASED_HEADER + '\n\n' + new_version_header
        )

    contents = contents.replace(
        unreleased_diff_link,
        new_unreleased_diff_link + '\n' + new_version_diff_link
        )

    return contents


def get_unreleased_notes(contents):
    '''
    Return the content of the "Unreleased" section of the given changelog.
    '''

    start = contents.index(UNRELEASED_HEADER) + len(UNRELEASED_HEADER) + 1
    end = RELEASE_HEADER_RE.search(contents).start() - 1

    return contents[start:end]
