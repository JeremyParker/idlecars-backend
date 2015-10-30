# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import inspect

from owner_crm.models import Campaign
from . import ops_messages, driver_messages, owner_messages, street_team_messages


def send(receiver_type, function_name, argument, receiver):
    function = '{}_messages.{}'.format(receiver_type, function_name)
    func = eval(function)

    campaign_name = '{}.{}'.format(receiver_type, function_name)

    campaign = Campaign.objects.filter(name=campaign_name).last()
    if not campaign:
        campaign = Campaign.objects.create(name=campaign_name)

    if not campaign:
        raise Exception('Campaign creation failed!!!')

    if campaign.preferred_medium is Campaign.SMS_MEDIUM and receiver.sms_enabled:
        medium = 'sms'
    else:
        medium = 'email'

    func(argument, medium)
