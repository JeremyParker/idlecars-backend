# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.core.urlresolvers import reverse
from django.utils import timezone

from owner_crm.services import ops_emails, driver_emails, owner_emails

from server.models import Booking


def conflicting_bookings(booking):
    return Booking.objects.filter(
        car=booking.car,
        state__in=[Booking.PENDING, Booking.FLAKE, Booking.COMPLETE],
    )


def send_reminders():
    # send reminders to drivers who started booking a car, and never submitted docs
    docs_reminder_delay_hours = 1  # TODO(JP): get from config

    reminder_threshold = timezone.now() - datetime.timedelta(hours=docs_reminder_delay_hours)
    remindable_bookings = Booking.objects.filter(
        state=Booking.PENDING,
        created_time__lte=reminder_threshold,
    )

    for booking in remindable_bookings:
        if not booking.driver.email():
            continue
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
        state=Booking.COMPLETE,
    )
    if not bookings:
        driver_emails.documents_approved_no_booking(driver)
        return

    for booking in bookings:
        driver_emails.documents_approved(booking)
        request_insurance(booking)


def someone_else_booked(booking):
    booking.state = Booking.TOO_SLOW
    driver_emails.someone_else_booked(booking)
    return booking


def request_insurance(booking):
    owner_emails.new_booking_email(booking)
    booking.state = Booking.REQUESTED
    booking.save()

    # cancel other conflicting in-progress bookings and notify those drivers
    for conflicting_booking in conflicting_bookings(booking):
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
        # TODO - driver_emails.new_booking_complete()
    else:
        booking.state = Booking.PENDING
    booking.save()

    ops_emails.new_booking_email(booking)
    return booking


def cancel_booking(booking):
    booking.state = Booking.CANCELED
    booking.save()
    return booking


def pre_save(modified_booking):
    if modified_booking.pk is not None:
        orig = Booking.objects.get(pk=modified_booking.pk)
    # TODO - check if it's being canceled. Then confirm the cancelation to the driver.
    # if the canceled booking was REQUESTED, then email the owner to tell them to cancel
    # the insurance request.
    return modified_booking
