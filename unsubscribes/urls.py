# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url

import views


urlpatterns = patterns('',
    url(r'^unsubscribes$', views.index, name='index'),
    url(r'^ununsubscribe$', views.ununsubscribe, name='ununsubscribe'),
)
