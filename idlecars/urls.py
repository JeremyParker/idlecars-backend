# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, include, url
from django.contrib import admin

import server.views

urlpatterns = patterns('',
    url(r'', include('website.urls', namespace='website')),

    url(r'^api/$', server.views.index, name='index'),

    url(r'^admin/', include(admin.site.urls)),
)
