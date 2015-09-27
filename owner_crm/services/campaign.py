# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from idlecars import email

from owner_crm.services import message as message_service


def send_to_queryset(queryset, func):
    campaign_name = func.__name__
    for obj in queryset.exclude(message__campaign=campaign_name,):
        func(obj)
        message_service.log_message(campaign_name, obj)
