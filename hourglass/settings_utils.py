import os
import json


def load_cups_from_vcap_services(name, env=os.environ):
    '''
    Detects if VCAP_SERVICES exists in the environment; if so, parses
    it and imports all the credentials from the given custom
    user-provided service (CUPS) as strings into the environment.

    For more details on CUPS, see:

    https://docs.cloudfoundry.org/devguide/services/user-provided.html
    '''

    if 'VCAP_SERVICES' not in env:
        return

    vcap = json.loads(env['VCAP_SERVICES'])

    for entry in vcap.get('user-provided', []):
        if entry['name'] == name:
            for key, value in entry['credentials'].items():
                env[key] = value


def get_whitelisted_ips(env=os.environ):
    '''
    Detects if WHITELISTED_IPS is in the environment; if not,
    returns None. if so, parses WHITELISTED_IPS as a comma-separated
    string and returns a list of values.
    '''
    if 'WHITELISTED_IPS' not in env:
        return None

    return [s.strip() for s in env['WHITELISTED_IPS'].split(',')]
