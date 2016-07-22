from django.conf import settings

from . import s70, fake_schedule


CHOICES = []

MODULES = {}


def register(module):
    CHOICES.append((module.__name__, module.TITLE))
    MODULES[module.__name__] = module


def load(choice, f):
    return MODULES[choice].load(f)


def serialize(pricelist):
    assert pricelist.__module__ in MODULES

    return (pricelist.__module__, pricelist.serialize())


def deserialize(data):
    module, d = data

    return MODULES[module].deserialize(d)


register(s70)

if settings.DEBUG:
    register(fake_schedule)
