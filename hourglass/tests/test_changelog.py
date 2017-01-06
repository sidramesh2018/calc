import os
import datetime
from unittest import TestCase
from semantic_version import Version
import markdown
from bs4 import BeautifulSoup

from ..version import __version__


repo_url = 'https://github.com/18F/calc'

my_dir = os.path.abspath(os.path.dirname(__file__))

changelog_path = os.path.normpath(
    os.path.join(my_dir, '..', '..', 'CHANGELOG.md'))

with open(changelog_path, 'r', encoding='utf-8') as f:
    changelog = BeautifulSoup(markdown.markdown(f.read()), 'html.parser')


def parsedate(s):
    return datetime.datetime.strptime(s, '%Y-%m-%d')


class ChangelogTests(TestCase):
    def test_changelog_has_unreleased_section(self):
        link = changelog.find('h2').find('a')
        self.assertEqual(link.get_text(), 'Unreleased')
        self.assertEqual(link.get('href'),
                         repo_url + '/compare/v%s...HEAD' % __version__)

    def test_latest_changelog_version_is_current_version(self):
        self.assertEqual(
            changelog.find_all('h2')[1].find('a').get_text(),
            __version__
            )

    def test_changelog_versions_and_dates_are_valid(self):
        version_headers = changelog.find_all('h2')[1:]

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
