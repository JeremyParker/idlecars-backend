# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import include, url
from django.conf import settings

import idlecars.routers

import views

router = idlecars.routers.OptionalApiRootDefaultRouter()
router.register(r'cars', views.CarViewSet, base_name='cars')
router.register(r'bookings', views.CreateBookingView, base_name='bookings')
router.register(r'drivers', views.UpdateDriverView, base_name='drivers')

urlpatterns = [
    url(r'^', include(router.urls)),
]
