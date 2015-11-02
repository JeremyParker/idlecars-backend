# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import inspect

from owner_crm.models import Campaign
from . import ops_messages, driver_messages, owner_messages, street_team_messages


def send(function_name, argument, receiver):
    func = eval(function_name)

    try:
        campaign = Campaign.objects.get(name=function_name)
    except Campaign.DoesNotExist:
        campaign = Campaign.objects.create(name=function_name)

    if campaign.preferred_medium is Campaign.SMS_MEDIUM and receiver.sms_enabled:
        medium = Campaign.SMS_MEDIUM
    else:
        medium = Campaign.EMAIL_MEDIUM

    func(argument, medium)
