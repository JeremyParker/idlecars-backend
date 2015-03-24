# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url
from django.contrib import admin

from . import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^survey/$', views.survey, name='survey'),
)
