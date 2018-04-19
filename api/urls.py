from django.conf.urls import url
from rest_framework.documentation import include_docs_urls

from api import views

urlpatterns = [
    url(r'^rates/$', views.GetRates.as_view()),
    url(r'^rates/csv/$', views.GetRatesCSV.as_view()),
    url(r'^search/$', views.GetAutocomplete.as_view()),
    url(r'^docs/', include_docs_urls(
        title='CALC API',
        description=(
            "For more developer documentation on CALC, please "
            "visit [/docs/](/docs/)."
        ),
    )),
]
