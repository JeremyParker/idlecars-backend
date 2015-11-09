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

def send_to_driver(queryset, campaign_name):
    for driver in queryset.exclude(message__campaign=campaign_name,):

        from server.services import booking as booking_service
        pending_bookings = booking_service.filter_pending(driver.booking_set)

        if pending_bookings:
            booking = pending_bookings.order_by('created_time').last()
            notification.send(campaign_name + 'Booking', booking)
        else:
            notification.send(campaign_name + 'Driver', driver)

        message_service.log_message(campaign_name, driver)
