# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from server.models import Driver
from server.services import credit_code as credit_code_service


def run_backfill_credit_codes():
    for driver in Driver.objects.filter(documentation_approved=True):
        code = credit_code_service.create_invite_code(driver.auth_user.customer)
        driver.auth_user.customer.invite_code = code
        driver.auth_user.customer.save()
        print('.')
