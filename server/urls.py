# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import include, url

from rest_framework.routers import DefaultRouter
from rest_framework.permissions import IsAdminUser

import views


class PrivateBrowsableDefaultRouter(DefaultRouter):
    '''
    Class to override permissions for the root API browser view
    '''
    def get_api_root_view(self):
        view = super(PrivateBrowsableDefaultRouter, self).get_api_root_view()
        view.cls.permission_classes = (IsAdminUser,)
        return view

router = PrivateBrowsableDefaultRouter()
router.register(r'cars', views.CarViewSet, base_name='cars')
router.register(r'bookings', views.CreateBookingView, base_name='bookings')

urlpatterns = [
    url(r'^', include(router.urls)),
]
