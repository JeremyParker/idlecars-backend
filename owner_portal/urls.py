# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

import views

urlpatterns = [
    url(r'^phone_numbers/(?P<pk>[0-9 ()+.\-]+)/$', views.PhoneNumberDetailView.as_view(), name='phone_numbers')
]
