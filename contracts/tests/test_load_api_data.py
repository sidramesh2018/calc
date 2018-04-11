import io
from django.core.management import call_command, CommandError
from django.test import LiveServerTestCase, TestCase

from contracts.mommy_recipes import get_contract_recipe
from contracts.models import Contract


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


class BasicTests(TestCase):
    def test_start_page_must_be_leq_end_page(self):
        msg = 'Start page cannot be greater than end page'
        with self.assertRaisesRegex(CommandError, msg):
            call_command('load_api_data', start_page=5, end_page=1)
