from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.db import transaction

BULK_UPLOAD_PERMISSION = 'contracts.add_bulkuploadcontractsource'
PRICE_LIST_UPLOAD_PERMISSION = 'data_capture.add_submittedpricelist'

ROLES = {}

# Devs: If any roles are added or modified, please also update
# the "Authentication and Authorization" section of README.md

ROLES['Data Administrators'] = set([
    'auth.add_user',
    'auth.change_user',
    BULK_UPLOAD_PERMISSION,
    'data_capture.change_submittedpricelist',
    'data_capture.change_submittedpricelistrow',
    'data_capture.change_newpricelist',
    'data_capture.change_approvedpricelist',
    'data_capture.change_unapprovedpricelist',
    'data_capture.change_rejectedpricelist',
])

ROLES['Contract Officers'] = set([
    PRICE_LIST_UPLOAD_PERMISSION,
    'data_capture.add_submittedpricelistrow',
])

# Data Administrators should also have any perms that Contract Officers do
ROLES['Data Administrators'].update(ROLES['Contract Officers'])


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


class Command(BaseCommand):
    help = '''\
    Initializes some helpful initial permission groups.
    '''

    def set_perms(self, groupname, perms):
        self.stdout.write("Setting permissions for group '%s'." % groupname)
        if self.verbosity >= 2:
            self.stdout.write("  Permissions: %s" % ', '.join(perms))
        try:
            group = Group.objects.get(name=groupname)
        except Group.DoesNotExist:
            self.stdout.write("  Group does not exist, creating it.")
            group = Group(name=groupname)
            group.save()
        group.permissions = get_permissions_from_ns_codenames(perms)
        group.save()

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.verbosity = int(kwargs['verbosity'])
        for groupname, perms in ROLES.items():
            self.set_perms(groupname, perms)
        self.stdout.write("Done.")
        self.stdout.write("Please do not manually change these "
                          "groups; they may be updated in the future.")
