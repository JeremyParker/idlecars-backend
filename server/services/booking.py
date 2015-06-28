# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from crm.services import ops_emails

from server.services import user_account as user_account_service
from server.services import driver as driver_service
from server.models import Booking


def create_booking(car, driver):
    '''
    Creates a new booking
    arguments
    - car: an existing car object
    - driver: the driver making the booking
    '''
    booking = Booking.objects.create(
        driver=driver,
        car=car,
    )
    ops_emails.new_booking_email(booking)
    return booking
