# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, include, url
from django.contrib import admin

from server import views
import web_app.urls

urlpatterns = patterns('',
    url(r'', include('website.urls', namespace='website')),

    url(r'^api/$', views.index, name='index'),

    url(r'^app/', include(web_app.urls)),

    url(r'^admin/', include(admin.site.urls)),
)
