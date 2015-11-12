# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from owner_crm.models import Campaign

def get_campaign(name):
    try:
        return Campaign.objects.get(name=name)
    except Campaign.DoesNotExist:
        return Campaign.objects.create(name=name)
