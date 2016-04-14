# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from owner_crm.models import ops_notifications, driver_notifications, owner_notifications


def send(campaign_name, argument, *args):
    clas = eval(campaign_name)(campaign_name, argument, *args)

    clas.send()
