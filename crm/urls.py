# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import include, url

import idlecars.routers

import views

router = idlecars.routers.OptionalApiRootDefaultRouter()
router.register(r'renewals', views.UpdateRenewalView, base_name='renewals')

urlpatterns = [
    url(r'^', include(router.urls)),
]
