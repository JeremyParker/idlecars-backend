# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import include, url

import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'cars', views.CarViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^$', views.api_root),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]