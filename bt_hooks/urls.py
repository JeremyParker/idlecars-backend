# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url

import views


urlpatterns = patterns('',
    url(r'^submerchant_create_success$', views.submerchant_create_success, name='submerchant_create_success'),
    url(r'^submerchant_create_failure$', views.submerchant_create_failure, name='submerchant_create_failure'),
)
