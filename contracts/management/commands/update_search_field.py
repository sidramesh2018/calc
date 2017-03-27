from djorm_pgfulltext.management.commands.update_search_field \
    import Command as UpdateSearchFieldCommand

from contracts.models import Contract


class Command(UpdateSearchFieldCommand):
    def handle(self, *args, **kwargs):
        '''
        This just shadows the djorm_pgfulltext command of the same
        name, modifying it so that we normalize the labor categories
        before updating the full-text search indexes.
        '''

        print("Updating normalized labor categories...")
        Contract.objects.bulk_update_normalized_labor_categories()

        print("Updating full-text search indexes...")
        super().handle(*args, **kwargs)
