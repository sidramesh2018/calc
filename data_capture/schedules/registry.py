from django.conf import settings
from django.utils.module_loading import import_string


def _classname(cls):
    return '%s.%s' % (cls.__module__, cls.__name__)


def _init():
    global CHOICES, CLASSES

    CHOICES = []
    CLASSES = {}

    for classname in settings.DATA_CAPTURE_SCHEDULES:
        cls = import_string(classname)
        CHOICES.append((classname, cls.title))
        CLASSES[classname] = cls


def load_from_upload(classname, f):
    return CLASSES[classname].load_from_upload(f)


def serialize(pricelist):
    classname = _classname(pricelist.__class__)
    assert classname in CLASSES

    return (classname, pricelist.serialize())


def deserialize(data):
    classname, d = data

    return CLASSES[classname].deserialize(d)


_init()
