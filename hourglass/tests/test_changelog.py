import datetime
from textwrap import dedent
from unittest import TestCase
from semantic_version import Version
from django.test import TestCase as DjangoTestCase
import markdown
from bs4 import BeautifulSoup

from ..version import __version__
from .. import changelog


repo_url = 'https://github.com/18F/calc'

changetext = changelog.get_contents()

changesoup = BeautifulSoup(markdown.markdown(changetext), 'html.parser')


def parsedate(s):
    return datetime.datetime.strptime(s, '%Y-%m-%d')


class UtilTests(TestCase):
    '''
    Tests for various changelog utility functions.
    '''

    BEFORE_BUMP = dedent('''
        ## [Unreleased][unreleased]

        - Fixed some stuff.

        ## 1.0.0 - 2017-01-02

        - Initial release.

        [unreleased]: https://github.com/foo/bar/compare/v1.0.0...HEAD
        ''')

    AFTER_BUMP = dedent('''
        ## [Unreleased][unreleased]

        ## [1.0.1][] - 2017-01-03

        - Fixed some stuff.

        ## 1.0.0 - 2017-01-02

        - Initial release.

        [unreleased]: https://github.com/foo/bar/compare/v1.0.1...HEAD
        [1.0.1]: https://github.com/foo/bar/compare/v1.0.0...v1.0.1
        ''')

    def test_bump_version_without_date_does_not_throw(self):
        changelog.bump_version(self.BEFORE_BUMP, '1.2.3')

    def test_bump_version_works(self):
        self.assertEqual(
            changelog.bump_version(self.BEFORE_BUMP, '1.0.1',
                                   datetime.date(2017, 1, 3)),
            self.AFTER_BUMP
            )

    def test_get_unreleased_notes_works(self):
        self.assertEqual(
            changelog.get_unreleased_notes(self.BEFORE_BUMP).strip(),
            '- Fixed some stuff.'
            )
        self.assertEqual(
            changelog.get_unreleased_notes(self.AFTER_BUMP).strip(),
            ''
            )

    def test_release_header_re_matches_unbracketed_version(self):
        self.assertEqual(
            changelog.RELEASE_HEADER_RE.search('## 1.2.3 ').group(1),
            '1.2.3'
            )

    def test_release_header_re_matches_bracketed_version(self):
        self.assertEqual(
            changelog.RELEASE_HEADER_RE.search('## [1.2.3][]').group(1),
            '1.2.3'
            )


class DjangoViewTests(DjangoTestCase):
    def test_it_works(self):
        res = self.client.get('/updates/')
        self.assertContains(res, 'Change Log')
        self.assertEqual(res.status_code, 200)


class ChangelogMdTests(TestCase):
    '''
    Tests to ensure the integrity of the existing CHANGELOG.md.
    '''

    def test_changelog_has_unreleased_section(self):
        self.assertIn(changelog.UNRELEASED_HEADER, changetext)
        self.assertEqual(
            changelog.get_unreleased_link(changetext),
            repo_url + '/compare/v%s...HEAD' % __version__
            )

    def test_latest_changelog_version_is_current_version(self):
        self.assertEqual(
            changelog.get_latest_release(changetext),
            __version__
            )

    def test_changelog_versions_and_dates_are_valid(self):
        version_headers = changesoup.find_all('h2')[1:]

        # The changelog lists versions reverse chronologically, but
        # we want to iterate through them chronologically.
        version_headers.reverse()

        last_version = None
        last_date = None

        self.assertGreater(len(version_headers), 1)

        for h in version_headers:
            version, date = h.get_text().split(' - ')
            if last_version is not None:
                self.assertLess(Version(last_version), Version(version))
                self.assertLess(parsedate(last_date), parsedate(date))
                self.assertEqual(
                    h.find('a').get('href'),
                    repo_url + '/compare/v%s...v%s' % (last_version, version)
                    )
            last_version = version
            last_date = date
