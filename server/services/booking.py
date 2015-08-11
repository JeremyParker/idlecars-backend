# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.core.urlresolvers import reverse
from django.utils import timezone

from owner_crm.services import ops_emails, driver_emails, owner_emails

from server.models import Booking
from server.services import car as car_service


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
    if Booking.REQUESTED == booking.state:
        owner_emails.booking_canceled(booking)

    booking.state = Booking.CANCELED
    booking.save()

    ops_emails.booking_canceled(booking)
    driver_emails.booking_canceled(booking)
    return booking


def start_time_display(booking):
    def _format_date(date):
        return date.strftime('%b %d')

    if booking.pick_up_time:
        time_string = _format_date(booking.pick_up_time)
    elif booking.approval_time:
        time_string = 'on pickup'
    elif booking.check_out_time:
        time_string = _format_date(booking.check_out_time + datetime.timedelta(days=2))
    else:
        time_string = _format_date(timezone.now() + datetime.timedelta(days=2))

    return time_string if booking.approval_time else time_string + ' (estimated)'


def min_rental_still_limiting(booking):
    min_notice = timezone.now() + datetime.timedelta(days=7)
    min_rental = car_service.get_min_rental_duration(booking.car)
    if not min_rental:
        return False

    if not booking.pick_up_time or booking.pick_up_time + datetime.timedelta(min_rental) > min_notice:
        return True
    return False


def first_valid_end_time(booking):
    '''
    Returns the earliest legal end time of the booking, so the user can't end the booking prematurely.
    The return value is a list of ints representing [Year, Zero-indexed month, Day].
    '''
    if min_rental_still_limiting(booking):
        min_rental_days = car_service.get_min_rental_duration(booking.car)
        return timezone.now() + datetime.timedelta(days=min_rental_days)
    return timezone.now() + datetime.timedelta(days=7)


def set_end_time(booking, end_time):
    booking.end_time = end_time
    booking.save()
    return booking
