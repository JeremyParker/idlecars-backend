# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url
from django.contrib import admin

from . import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^driver/$', views.index, name="driver_endpoint"),
    url(r'^owner/$', views.index, name="owner_endpoint"),
    url(r'^driver_survey/(\d+)$', views.driver_survey, name='driver_survey'),
    url(r'^owner_survey/(\d+)$', views.owner_survey, name='owner_survey'),
    url(r'^thankyou/$', views.thankyou, name='thankyou'),
)
