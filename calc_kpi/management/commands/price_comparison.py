from django.core.management import BaseCommand
from optparse import make_option
from contracts.models import Contract
import math
#super useful / interesting stackoverflow:
# http://stackoverflow.com/questions/23251759/how-to-determine-what-is-the-probability-distribution-function-from-a-numpy-arra

#The goal of this code is to figure out how many contracts cost more than an input contract cost

#Inputs:
# hourly rate
# labor category

#Outputs:
# percentage of contracts with a higher hourly rate for the given labor category
class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option(
            '--labor_category',
            help='python manage.py price_comparison --labor_category [LABOR CATEGORY] --hourly_rate [HOURLY RATE]'
        ),make_option(
            '--hourly_rate',
            help='python manage.py price_comparison --labor_category [LABOR CATEGORY] --hourly_rate [HOURLY RATE]'
        ),
    )

    def handle(self, *args, **options):
        print("Labor category entered:",options["labor_category"])
        print("Hourly year 1 rate entered:",options["hourly_rate"])
        results = Contract.objects.filter(labor_category=options["labor_category"])
        total_results = len(results)
        hourly_rate = float(options["hourly_rate"])
        count_with_higher_price = len([result for result in results if result.hourly_rate_year1 > hourly_rate])
        percentage = math.floor(100 * (float(count_with_higher_price)/total_results))
        print("Percentage with higer hourly year 1 rates:", percentage)
            
