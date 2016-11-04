from django.conf.urls import url

from . import views, ajaxform_example, date_example, radio_checkbox_example


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^ajaxform$', ajaxform_example.view, name='ajaxform'),
    url(r'^date$', date_example.view, name='date'),
    url(r'^radio-checkbox$', radio_checkbox_example.view,
        name='radio-checkbox'),
]
