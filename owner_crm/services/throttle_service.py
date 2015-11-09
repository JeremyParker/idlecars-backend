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

def send_to_owner(queryset, campaign_name):
    for obj in queryset.exclude(message__campaign=campaign_name,):
        notification.send(campaign_name, obj)
        message_service.log_message(campaign_name, obj)

def send_to_driver(queryset, campaign_name):
    for driver in queryset.exclude(message__campaign=campaign_name,):
        message_service.log_message(campaign_name, driver)

        # this is a special-case for the document reminder emails.
        if 'DocumentsReminder' in campaign_name:
            from server.services import booking as booking_service
            pending_bookings = booking_service.filter_pending(driver.booking_set)
            if pending_bookings:
                booking = pending_bookings.order_by('created_time').last()
                notification.send(campaign_name + 'Booking', booking)
            else:
                notification.send(campaign_name + 'Driver', driver)
