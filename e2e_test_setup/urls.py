# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url
from django.conf import settings

from . import views

if hasattr(settings, 'WARNING__ENABLE_TEST_SETUP_ENDPOINT__TEST_MODE_ONLY') and settings.WARNING__ENABLE_TEST_SETUP_ENDPOINT__TEST_MODE_ONLY:
    urlpatterns = patterns('',
        url(r'^e2e_test_setup$', views.e2e_test_setup, name='e2e_test_setup'),
        url(r'^e2e_test_docs_approve$', views.e2e_test_docs_approve, name='e2e_test_docs_approve'),
        url(r'^e2e_test_insurance_approve$', views.e2e_test_insurance_approve, name='e2e_test_insurance_approve'),
    )
else:
    urlpatterns = patterns('')
