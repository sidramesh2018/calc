import doctest

from .. import models


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(models))
    return tests
