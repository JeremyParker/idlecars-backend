# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse
from django.conf import settings

def e2e_test_setup(request):
    if settings.WARNING__ENABLE_TEST_SETUP_ENDPOINT__TEST_MODE_ONLY:
        # NOTE: do the bad stuff here
        return JsonResponse({})
    else:
        return JsonResponse({}, status_code=400)
