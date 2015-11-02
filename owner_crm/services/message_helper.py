# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import inspect

from owner_crm.models import Campaign
from . import ops_messages, driver_messages, owner_messages, street_team_messages


def send(function_name, argument, receiver):
    func = eval(function_name)

    campaign = Campaign.objects.filter(name=function_name).last()
    if not campaign:
        campaign = Campaign.objects.create(name=function_name)

    if not campaign:
        raise Exception('Campaign creation failed!!!')

    if campaign.preferred_medium is Campaign.SMS_MEDIUM and receiver.sms_enabled:
        medium = 'sms'
    else:
        medium = 'email'

    func(argument, medium)
