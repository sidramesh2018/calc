from django.core.management import call_command
from django.test import LiveServerTestCase

from contracts.mommy_recipes import get_contract_recipe
from contracts.models import Contract


class LoadApiDataTestCase(LiveServerTestCase):
    def test_appending_from_self_doubles_contract_count(self):
        count = 5
        get_contract_recipe().make(_quantity=count)
        call_command(
            'load_api_data',
            url=f"{self.live_server_url}/api/rates/",
            append=True
        )
        self.assertEquals(Contract.objects.count(), count * 2)
