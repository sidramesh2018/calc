DEBUG=True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'hourglass',
        'USER': '',
        'PASSWORD': '',
    }
}

SECRET_KEY = 'lty$v06r9%dy!*@4#pc)u$+dasqn4we!%(9xgp3n=psp*d72rm'

# for front-end testing with Sauce
REMOTE_TESTING = {
    'enabled': False,
    'hub_url': 'http://%s:%s@ondemand.saucelabs.com:80/wd/hub',
    'username': '',
    'access_key': '',
    'capabilities': {
        # 'browser': 'internet explorer',
        # 'version': '9.0',
        # 'platform': 'Windows 7'
    }
}


SECURE_SSL_REDIRECT = False
