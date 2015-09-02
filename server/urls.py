# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import include, url
from django.conf import settings

from rest_framework.authtoken import views as auth_views

import idlecars.routers
import views

router = idlecars.routers.OptionalApiRootDefaultRouter()
router.register(r'cars', views.CarViewSet, base_name='cars')
router.register(r'bookings', views.BookingViewSet, base_name='bookings')
router.register(r'drivers', views.DriverViewSet, base_name='drivers')
router.register(r'owners', views.OwnerViewSet, base_name='owners')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^token-auth/', auth_views.obtain_auth_token, name='token-auth'),
    url(r'^phone_numbers/(?P<pk>[0-9 ()+.\-]+)/$', views.PhoneNumberDetailView.as_view(), name='phone_numbers'),
    url(r'^owner_phone_numbers/(?P<pk>[0-9 ()+.\-]+)/$', views.OwnerPhoneNumberDetailView.as_view(), name='owner_phone_numbers'),
]
