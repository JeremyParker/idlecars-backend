# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from idlecars import email

from owner_crm.services import message as message_service
from owner_crm.services import notification


def throttle(queryset, campaign_name):
    return queryset.exclude(message__campaign=campaign_name,)


def mark_sent(throttled_queryset, campaign_name):
    for obj in throttled_queryset:
        message_service.log_message(campaign_name, obj)
