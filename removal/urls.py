# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import include, url

import idlecars.routers
from removal import views

router = idlecars.routers.OptionalApiRootDefaultRouter()
router.register(r'removals', views.RemovalViewSet, base_name='removals')
urlpatterns = [url(r'^', include(router.urls))]
