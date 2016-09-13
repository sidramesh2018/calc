from django.conf.urls import include, url

from .views import price_list_upload, bulk_upload

urlpatterns = [
    url(r'^step/', include(price_list_upload.steps.urls)),
    url(r'^bulk/region-10/step/', include(bulk_upload.steps.urls)),
]
