# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from server.models import Driver
from credit import credit_service


def run_backfill_credit_codes():
    '''
    Add an invitation CreditCode for every driver that has submitted docuements
    '''
    for driver in Driver.objects.filter(documentation_approved=True):
        # TODO - these values shuold come from an A/B test not from settings
        code = credit_service.create_invite_code(
            settings.SIGNUP_CREDIT,
            settings.INVITOR_CREDIT,
            driver.auth_user.customer,
        )
        print('.')
