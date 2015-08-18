# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse
from django.conf import settings

import models
from server.models.driver import Driver
from server.models.booking import Booking

def e2e_test_setup(request):
    if settings.WARNING__ENABLE_TEST_SETUP_ENDPOINT__TEST_MODE_ONLY:
        models.E2ETestSetup().perform()
        return JsonResponse({})
    else:
        return JsonResponse({}, status_code=400)
