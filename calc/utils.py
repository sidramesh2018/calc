from django.contrib.auth.models import Permission


def get_permissions_from_ns_codenames(ns_codenames):
    '''
    Returns a list of Permission objects for the specified namespaced codenames
    '''
    splitnames = [ns_codename.split('.') for ns_codename in ns_codenames]
    return [
        Permission.objects.get(codename=codename,
                               content_type__app_label=app_label)
        for app_label, codename in splitnames
    ]
