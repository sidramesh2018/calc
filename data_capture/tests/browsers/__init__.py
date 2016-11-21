import os

from .robobrowser import RoboBrowserTestCase
from .selenium import SeleniumTestCase


if 'WD_TESTING_BROWSER' in os.environ:
    BrowserTestCase = SeleniumTestCase
else:
    BrowserTestCase = RoboBrowserTestCase
