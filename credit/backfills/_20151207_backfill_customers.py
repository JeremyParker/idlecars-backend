# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from credit.models import Customer

def run_backfill_customers():
    User = get_user_model()
    for user in User.objects.all():
        Customer.objects.get_or_create(user=user)
        print('.')
