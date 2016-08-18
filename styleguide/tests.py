from django.test import TestCase, override_settings

from hourglass.urls import urlpatterns, styleguide_url


urlpatterns += [styleguide_url]


@override_settings(ROOT_URLCONF=__name__)
class StyleguideTests(TestCase):

    def test_styleguide_returns_200(self):
        response = self.client.get('/styleguide/')
        self.assertEqual(response.status_code, 200)

    def test_styleguide_ajaxform_returns_200(self):
        response = self.client.get('/styleguide/ajaxform')
        self.assertEqual(response.status_code, 200)
