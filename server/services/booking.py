# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.core.urlresolvers import reverse
from django.utils import timezone

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
    )
    booking = state_machine.on_created(booking)
    return booking


def send_reminders():
    # send reminders to drivers who started booking a car, and never submitted docs
    docs_reminder_delay_hours = 24  # TODO(JP): get from config

    reminder_threshold = timezone.now() - datetime.timedelta(hours=docs_reminder_delay_hours)
    remindable_bookings = Booking.objects.filter(
        state=Booking.PENDING,
        created_time__lte=reminder_threshold,
    )

    for booking in remindable_bookings:
        booking = state_machine.on_delay_passed(booking)
        booking.save()


def on_documents_uploaded(driver):
    bookings = Booking.objects.filter(
        driver=driver,
        state__in=[Booking.PENDING, Booking.FLAKE]
    )
    for booking in bookings:
        booking = state_machine.on_documents_uploaded(booking)
        booking.save()


def on_documents_approved(driver):
    bookings = Booking.objects.filter(
        driver=driver,
        state_in=Booking.COMPLETE,
    )
    if not bookings:
        driver_emails.documents_approved_no_booking(driver)
        return

    for booking in bookings:
        booking = state_machine.on_documents_approved(booking)

        # cancel other conflicting in-progress bookings and notify those drivers
        conflicting_bookings = Booking.objects.filter(
            car=booking.car,
            state__in=[Booking.PENDING, Booking.FLAKE, Booking.COMPLETE],
        )
        for conflicting_booking in conflicting_bookings:
            conflicting_booking = state_machine.on_someone_else_booked(conflicting_booking)
            conflicting_booking.save()
