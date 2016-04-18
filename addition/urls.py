# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import include, url

import idlecars.routers
from addition import views

router = idlecars.routers.OptionalApiRootDefaultRouter()
router.register(r'additions', views.AdditionViewSet, base_name='additions')
urlpatterns = [url(r'^', include(router.urls))]
