# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url
from django.contrib import admin

from . import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^driver_prospect/(\d+)/driver_survey/new$', views.driver_survey, name='driver_survey'),
    url(r'^owner_prospect/(\d+)/owner_survey/new$', views.owner_survey, name='owner_survey'),
    url(r'^thankyou/$', views.thankyou, name='thankyou'),
)
