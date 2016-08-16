from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^step/1$', views.step_1, name='step_1'),
    url(r'^step/2$', views.step_2, name='step_2'),
    url(r'^step/3$', views.step_3, name='step_3'),
    url(r'^step/4$', views.step_4, name='step_4'),
]
