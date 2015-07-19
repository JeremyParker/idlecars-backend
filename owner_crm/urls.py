# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import include, url

import idlecars.routers

import views

router = idlecars.routers.OptionalApiRootDefaultRouter()
router.register(r'renewals', views.UpdateRenewalView, base_name='renewals')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^password/reset_setup/$', views.PasswordResetSetups.as_view(), name='password_setups'),
    url(r'^password/reset_execute/$', views.PasswordResetExecutions.as_view(), name='password_executions'),
    url(r'^email_preview/([a-zA-Z0-9_]+)$', views.email_preview, name='email_preview'),
]
