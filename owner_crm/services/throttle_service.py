# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from idlecars import email

from owner_crm.services import message as message_service
from owner_crm.services import notification


def send_to_queryset(queryset, func):
    campaign_name = func.__name__
    for obj in queryset.exclude(message__campaign=campaign_name,):
        func(obj)
        message_service.log_message(campaign_name, obj)

def send_to_owner(queryset, campaign_name):
    campaign_name = campaign_name
    for obj in queryset.exclude(message__campaign=campaign_name,):
        notification.send(campaign_name, obj)
        message_service.log_message(campaign_name, obj)
