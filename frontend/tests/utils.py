from django.conf import settings
from django.core import management

import subprocess


_static_assets_built = False
_static_asset_prereqs_built = False


def build_static_asset_prerequisites():
    '''
    Builds prerequisites for Django's static asset collection (e.g.,
    JS and CSS bundles).
    '''

    global _static_asset_prereqs_built

    if not _static_asset_prereqs_built:
        subprocess.check_call(['npm', 'run', 'gulp', '--', 'build'])
        _static_asset_prereqs_built = True


def remove_static_assets():
    '''
    Removes folder Django is currently configured to collect
    static assets in.
    '''

    subprocess.check_call(['rm', '-rf', settings.STATIC_ROOT])


def build_static_assets():
    '''
    Sometimes we need static assets to be available before browser-based
    tests run. We want to be able to have multiple browser-based test suites,
    but we also don't want to needlessly regenerate the static assets
    for each one, so we'll use this function, which ensures that the assets
    are only built once per test run.
    '''

    global _static_assets_built

    build_static_asset_prerequisites()

    if not _static_assets_built:
        remove_static_assets()
        management.call_command('collectstatic', '--noinput', '--link',
                                verbosity=0)
        _static_assets_built = True
