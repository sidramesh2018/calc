import unittest
import doctest

from .. import views


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(views))
    return tests
