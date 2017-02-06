from unittest import TestCase
import requests
from robobrowser import RoboBrowser


class CfHttpClient:
    '''
    A basic HTTP client that defaults to the given origin.
    '''

    def __init__(self, origin):
        self.origin = origin

    def get(self, url, *args, **kwargs):
        if url.startswith('/'):
            url = self.origin + url
        if 'allow_redirects' not in kwargs:
            kwargs['allow_redirects'] = False
        return requests.get(url, *args, **kwargs)


class CfBrowser(RoboBrowser):
    '''
    A RoboBrowser subclass that defaults to the given origin.
    '''

    def __init__(self, origin, *args, **kwargs):
        self.origin = origin
        super().__init__(*args, **kwargs)

    def open(self, url):
        if url.startswith('/'):
            url = self.origin + url
        return super().open(url)


class CfTestCase(TestCase):
    '''
    A base test case whose utilities default to a production deployment
    of CALC.
    '''

    ORIGIN = 'https://calc.gsa.gov'

    def setUp(self):
        self.client = CfHttpClient(self.ORIGIN)
        self.browser = CfBrowser(self.ORIGIN, history=True,
                                 parser='html.parser')
