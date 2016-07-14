from django.core.management.base import BaseCommand


class Command(BaseCommand):
    '''
    Test and lint everything all at once.
    '''

    def handle(self, *args, **options):
        print("THIS IS THE ULTRATEST")
