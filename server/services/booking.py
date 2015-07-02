# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.core.urlresolvers import reverse
from django.utils import timezone

from crm.services import ops_emails, driver_emails, owner_emails

from server.services import driver as driver_service
from server.services import _booking_state_machine as state_machine
from server.models import Booking


def send_reminders():
    # send reminders to drivers who started booking a car, and never submitted docs
    docs_reminder_delay_hours = 24  # TODO(JP): get from config

    reminder_threshold = timezone.now() - datetime.timedelta(hours=docs_reminder_delay_hours)
    remindable_bookings = Booking.objects.filter(
        state=Booking.PENDING,
        created_time__lte=reminder_threshold,
    )

    for booking in remindable_bookings:
        driver_emails.documents_reminder(booking)
        booking.state = Booking.FLAKE
        booking.save()


def on_documents_uploaded(driver):
    # note: the driver service sends ops an email to check the docs
    bookings = Booking.objects.filter(
        driver=driver,
        state__in=[Booking.PENDING, Booking.FLAKE]
    )
    for booking in bookings:
        booking.state = Booking.COMPLETE
        booking.save()
        return booking


def on_documents_approved(driver):
    bookings = Booking.objects.filter(
        driver=driver,
        state_in=Booking.COMPLETE,
    )
    if not bookings:
        driver_emails.documents_approved_no_booking(driver)
        return

    for booking in bookings:
        driver_emails.documents_approved(booking)
        request_insurance(booking)


def someone_else_booked(booking):
    booking.state = Booking.TOO_SLOW
    driver_email.someone_else_booked(booking)
    return booking


def request_insurance(booking):
    owner_emails.new_booking_email(booking)
    booking.state = Booking.REQUESTED

    # cancel other conflicting in-progress bookings and notify those drivers
    conflicting_bookings = Booking.objects.filter(
        car=booking.car,
        state__in=[Booking.PENDING, Booking.FLAKE, Booking.COMPLETE],
    )
    for conflicting_booking in conflicting_bookings:
        conflicting_booking = someone_else_booked(conflicting_booking)
        conflicting_booking.save()

    return booking


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

    if booking.driver.documentation_approved:
        # TODO - driver_emails.new_booking_insurance_requested()
        return request_insurance(booking)

    if booking.driver.all_docs_uploaded():
        booking.state = Booking.COMPLETE
    else:
        booking.state = Booking.PENDING
    booking.save()

    ops_emails.new_booking_email(booking)
    # TODO - driver_emails.new_booking()
    return booking
