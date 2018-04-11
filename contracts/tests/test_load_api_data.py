import io
from django.core.management import call_command, CommandError
from django.test import LiveServerTestCase, SimpleTestCase, override_settings
from httmock import all_requests, response, HTTMock

from contracts.mommy_recipes import get_contract_recipe
from contracts.models import Contract
from contracts.management.commands.load_api_data import iter_api_pages


class LiveServerTests(LiveServerTestCase):
    def test_loading_from_empty_db_works(self):
        stdout = io.StringIO()
        call_command(
            'load_api_data',
            url=f"{self.live_server_url}/api/rates/",
            append=True,
            stdout=stdout
        )
        self.assertRegex(
            stdout.getvalue(),
            f'No rates were written to the database'
        )

    @override_settings(PAGINATION=2)
    def test_retrieving_multiple_pages_works(self):
        get_contract_recipe().make(_quantity=5)
        stdout = io.StringIO()
        call_command(
            'load_api_data',
            url=f"{self.live_server_url}/api/rates/",
            dry_run=True,
            stdout=stdout
        )
        self.assertRegex(
            stdout.getvalue(),
            'Processed 5 rates in dry run mode over 3 pages'
        )

    @override_settings(PAGINATION=2)
    def test_stops_retrieving_at_end_page(self):
        get_contract_recipe().make(_quantity=5)
        stdout = io.StringIO()
        call_command(
            'load_api_data',
            url=f"{self.live_server_url}/api/rates/",
            dry_run=True,
            end_page=1,
            stdout=stdout
        )
        self.assertRegex(
            stdout.getvalue(),
            'Processed 2 rates in dry run mode over 1 pages'
        )

    def test_appending_from_self_doubles_contract_count(self):
        count = 5
        get_contract_recipe().make(_quantity=count)
        stdout = io.StringIO()
        call_command(
            'load_api_data',
            url=f"{self.live_server_url}/api/rates/",
            append=True,
            stdout=stdout
        )
        self.assertEquals(Contract.objects.count(), count * 2)
        self.assertRegex(
            stdout.getvalue(),
            f'Done writing {count} rates to the database'
        )


def json_200(content):
    @all_requests
    def response_content(url, request):
        headers = {'content-type': 'application/json'}
        return response(200, content, headers)

    return response_content


EMPTY_RESPONSE = {
    'count': 0,
    'results': [],
    'next': None,
}


CONTRACT = {
    'id': 123,
    'foo': 'blah',
}


class SimpleTests(SimpleTestCase):
    def test_start_page_must_be_leq_end_page(self):
        msg = 'Start page cannot be greater than end page'
        with self.assertRaisesRegex(CommandError, msg):
            call_command('load_api_data', start_page=5, end_page=1)

    def test_results_are_ok(self):
        res = {**EMPTY_RESPONSE, 'results': [CONTRACT]}
        with HTTMock(json_200(res)):
            results, total = next(iter_api_pages('http://blah'))
            self.assertEqual(results, [{'foo': 'blah'}])

    def test_total_pages_is_correct_when_end_page_is_too_high(self):
        with HTTMock(json_200(EMPTY_RESPONSE)):
            results, total = next(iter_api_pages('http://blah', end_page=99))
            self.assertEqual(total, 1)
