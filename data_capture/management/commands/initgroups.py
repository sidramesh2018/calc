from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


ROLES = {}

ROLES['Data Administrators'] = (
    'add_user',
    'change_user',
    'change_submittedpricelist',
    'change_submittedpricelistrow',
)


class Command(BaseCommand):
    help = '''\
    Initializes some helpful initial permission groups.
    '''

    def set_perms(self, groupname, codenames):
        self.stdout.write("Setting permissions for group '%s'." % groupname)
        if self.verbosity >= 2:
            self.stdout.write("  Permissions: %s" % ', '.join(codenames))
        try:
            group = Group.objects.get(name=groupname)
        except Group.DoesNotExist:
            group = Group(name=groupname)
            group.save()
        group.permissions = [
            Permission.objects.get(codename=codename)
            for codename in codenames
        ]
        group.save()

    def handle(self, *args, **kwargs):
        self.verbosity = int(kwargs['verbosity'])
        for groupname, codenames in ROLES.items():
            self.set_perms(groupname, codenames)
        self.stdout.write("Done.")
        self.stdout.write("Please do not manually change these "
                          "groups; they may be updated in the future.")
