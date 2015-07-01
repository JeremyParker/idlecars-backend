# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from crm.services import ops_emails, driver_emails, owner_emails

from server.services import driver as driver_service
from server.services import _booking_state_machine as state_machine
from server.models import Booking


def create_booking(car, driver):
    '''
    Creates a new booking
    arguments
    - car: an existing car object
    - driver: the driver making the booking
    '''
    booking = Booking(
        car=car,
        driver=driver,
        state=0,
    )
    booking = state_machine.update(booking, state_machine.CREATED)
    booking.save()
    return booking


def on_documents_uploaded(driver):
    bookings = Booking.objects.filter(
        driver=driver,
        state__in=[Booking.PENDING, Booking.FLAKE]
    )
    for booking in bookings:
        booking = state_machine.update(booking, state_machine.DOCUMENTS_APPROVED)
        booking.save()


def on_documents_approved(driver):
    bookings = Booking.objects.filter(
        driver=driver,
        state=Booking.COMPLETE,
    )
    if bookings:
        for booking in bookings:
            booking = state_machine.update(booking, state_machine.DOCUMENTS_APPROVED)

            # cancel other conflicting in-progress bookings and notify those drivers
            conflicting_bookings = Booking.objects.filter(
                car=booking.car,
                state__in=[Booking.PENDING, Booking.FLAKE, Booking.COMPLETE],
            ).exclude(
                driver=driver,
            )
            for conflicting_booking in conflicting_bookings:
                conflicting_booking = state_machine.update(conflicting_booking, SOMEONE_ELSE_BOOKED)
                conflicting_booking.save()
    else:
        driver_emails.documents_approved_no_booking(driver)
