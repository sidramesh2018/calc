from django.conf.urls import include, url

from .views import price_list_upload, bulk_upload

urlpatterns = [
    url(r'^step/', include(price_list_upload.steps.urls)),

    url(r'^bulk/region-10/step/1$',
        bulk_upload.region_10_step_1, name="bulk_region_10_step_1"),
    url(r'^bulk/region-10/step/2$',
        bulk_upload.region_10_step_2, name="bulk_region_10_step_2"),
    url(r'^bulk/region-10/step/3$',
        bulk_upload.region_10_step_3, name="bulk_region_10_step_3"),
]
