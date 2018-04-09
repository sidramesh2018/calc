import requests
from django.core.management import BaseCommand

from contracts.models import Contract
from api.serializers import ContractSerializer


def iter_api_pages(url, start_page=1, end_page=None):
    page = start_page
    i = 0
    while True:
        if end_page is not None and page > end_page:
            break
        res = requests.get(f"{url}?page={page}").json()
        results = res['results']
        for result in results:
            del result['id']
        i += len(results)
        yield results, i, res['count']
        if res['next'] is not None:
            page += 1
        else:
            break


class Command(BaseCommand):
    help = "Load rate data from the API of another CALC instance."

    DEFAULT_URL = "https://api.data.gov/gsa/calc/rates/"

    def add_arguments(self, parser):
        parser.add_argument(
            '-s', '--start-page',
            default=1,
            type=int,
            help='start page (default is 1)'
        )

        parser.add_argument(
            '-e', '--end-page',
            default=None,
            type=int,
            help='end page (default is to read all pages)'
        )

        parser.add_argument(
            '--append',
            default=False,
            action='store_true',
            help='append to existing rates (instead of deleting them first)'
        )

        parser.add_argument(
            '-u', '--url',
            default=self.DEFAULT_URL,
            help=f'URL of CALC API (default is {self.DEFAULT_URL})'
        )

    def handle(self, *args, **options):
        url = options['url']

        if not options['append']:
            self.stdout.write("Deleting all existing rate information.")
            Contract.objects.all().delete()

        self.stdout.write(f"Loading new rate information from {url}.")

        start_page = options['start_page']
        end_page = options['end_page']
        pagenum = start_page
        for rates, i, total in iter_api_pages(url, start_page, end_page):
            serializer = ContractSerializer(data=rates, many=True)
            if serializer.is_valid():
                serializer.save()
            else:
                for rate, error in zip(rates, serializer.errors):
                    if not error:
                        continue
                    self.stdout.write(
                        f"Rate {self.style.WARNING(rate)} has "
                        f"error {self.style.ERROR(error)}!"
                    )
            self.stdout.write(
                f"Processed {i} of {total} rates (page {pagenum}).")
            pagenum += 1

        self.stdout.write(self.style.SUCCESS(
            f"Done writing {i} rates to the database."))
