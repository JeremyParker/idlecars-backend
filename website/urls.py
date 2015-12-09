# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^about$', views.about, name='about'),
    url(r'^contact/(\d+)/driver_survey/new$', views.driver_survey, name='driver_survey'),
    url(r'^contact/(\d+)/owner_survey/new$', views.owner_survey, name='owner_survey'),
    url(r'^(?P<credit>[0-9]{2})$', views.driver_referral, name='driver_referral'),
)
