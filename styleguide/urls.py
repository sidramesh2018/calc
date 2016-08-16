from django.conf.urls import patterns, url

from . import views, ajaxform_example, date_example


urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'^ajaxform$', ajaxform_example.view, name='ajaxform'),
    url(r'^date$', date_example.view, name='date'),
)
