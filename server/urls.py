# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import include, url

from rest_framework.routers import DefaultRouter

import views

router = DefaultRouter()
router.register(r'cars', views.CarViewSet, base_name='cars')
router.register(r'bookings', views.CreateBookingView, base_name='bookings')


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^$', views.api_root),  # TODO - remove this as redundant?
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
