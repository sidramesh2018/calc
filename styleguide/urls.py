from django.conf.urls import url

from . import views, ajaxform_example


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^ajaxform$', ajaxform_example.view, name='ajaxform'),
]
