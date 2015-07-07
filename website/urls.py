# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^contact/(\d+)/driver_survey/new$', views.driver_survey, name='driver_survey'),
    url(r'^contact/(\d+)/owner_survey/new$', views.owner_survey, name='owner_survey'),
)
