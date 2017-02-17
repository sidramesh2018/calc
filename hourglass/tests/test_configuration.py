import os
from unittest import TestCase
import json
import yaml


MY_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.normpath(os.path.join(MY_DIR, '..', '..'))


def path(*x):
    return os.path.join(ROOT_DIR, *x)


class Version:
    '''
    Just a helper that makes it easy to do things with version numbers.

        >>> v = Version('1.2.3')
        >>> str(v)
        '1.2.3'
        >>> float(v)
        1.2
    '''

    def __init__(self, version):
        self.parts = version.split('.')

    def __str__(self):
        return '.'.join(self.parts)

    def __float__(self):
        return float('.'.join(self.parts[:2]))


class PythonVersionTests(TestCase):
    '''
    Ensure all our configuration files, documentation, etc. specify the
    same Python version.
    '''

    version = Version('3.6.0')

    def test_runtime_txt(self):
        with open(path('runtime.txt')) as f:
            self.assertEqual(f.read().strip(),
                             'python-{}'.format(self.version))

    def test_dockerfile(self):
        with open(path('Dockerfile')) as f:
            self.assertIn('FROM python:{}'.format(self.version),
                          f.read())

    def test_travis_yml(self):
        with open(path('.travis.yml')) as f:
            data = yaml.safe_load(f)
            self.assertEqual(data['python'], [float(self.version)])

    def test_docs_setup_md(self):
        with open(path('docs', 'setup.md')) as f:
            self.assertIn(f'Python {self.version}', f.read())


class NodeVersionTests(TestCase):
    '''
    Ensure all our configuration files, documentation, etc. specify
    the same Node version.
    '''

    version = Version('6.0')

    def test_package_json(self):
        with open(path('package.json')) as f:
            package = json.load(f)
            min_version = package['engines']['node'].split()[0]
            self.assertEqual(min_version, f'>={self.version}')

    def test_docs_setup_md(self):
        with open(path('docs', 'setup.md')) as f:
            self.assertIn(f'Node {self.version}', f.read())
