# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from server.models import Driver
from server.services import driver as driver_service

def run_backfill_credit_codes():
    '''
    Add an invitation CreditCode for every driver that has submitted documents
    '''
    for driver in Driver.objects.filter(documentation_approved=True):
        driver_service.assign_credit_code(driver)
        print('.')
