# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from owner_crm.services import ops_emails, driver_emails, owner_emails

from server.models import Booking

''' These are the states where the user sees the booking in their bookings page '''
visible_states = [
    Booking.PENDING,
    Booking.COMPLETE,
    Booking.REQUESTED,
    Booking.ACCEPTED,
    Booking.BOOKED,
    Booking.FLAKE,
]

cancelable_states = [
    Booking.PENDING,
    Booking.COMPLETE,
    Booking.REQUESTED,
    Booking.FLAKE,
]

def conflicting_bookings(booking):
    return Booking.objects.filter(
        car=booking.car,
        state__in=[Booking.PENDING, Booking.FLAKE, Booking.COMPLETE],
    )


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
    if Booking.REQUESTED == booking.state:
        owner_emails.booking_canceled(booking)

    booking.state = Booking.CANCELED
    booking.save()

    ops_emails.booking_canceled(booking)
    driver_emails.booking_canceled(booking)
    return booking
