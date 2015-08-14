# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.core.urlresolvers import reverse
from django.utils import timezone

from owner_crm.services import ops_emails, driver_emails, owner_emails

from server.models import Booking, booking_state
from server.services import car as car_service


def conflicting_pending_bookings(booking):
    return Booking.objects.filter(
        car=booking.car,
        state__in=[Booking.PENDING, Booking.FLAKE],
    )


def is_visible(booking):
    ''' Can this booking be seen in the Driver app '''
    return booking_state.state[booking.state]['visible']


def can_cancel(booking):
    return booking_state.state[booking.state]['cancelable']


def can_checkout(booking):
    # TODO - check that the car is still available (may have been a race to book)
    return booking.driver.all_docs_uploaded() and \
        booking_state.state[booking.state]['checkoutable']


def can_pickup(booking):
    return booking.driver.documentation_approved and \
        booking_state.state[booking.state]['pickupable']


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


def on_documents_approved(driver):
    bookings = Booking.objects.filter(
        driver=driver,
        state__in=[Booking.PENDING, Booking.FLAKE]
    )
    if not bookings:
        driver_emails.documents_approved_no_booking(driver)
        return

    for booking in bookings:
        driver_emails.documents_approved(booking)
        request_insurance(booking)


def someone_else_booked(booking):
    booking.state = Booking.TOO_SLOW
    booking.incomplete_time = timezone.now()
    booking.incomplete_reason = Booking.REASON_ANOTHER_BOOKED
    booking.save()
    driver_emails.someone_else_booked(booking)
    return booking


def request_insurance(booking):
    owner_emails.new_booking_email(booking)
    # TODO - driver_emails.new_booking_insurance_requested()
    booking.state = Booking.REQUESTED
    booking.requested_time = timezone.now()
    booking.save()

    # cancel other conflicting in-progress bookings and notify those drivers
    for conflicting_booking in conflicting_pending_bookings(booking):
        conflicting_booking = someone_else_booked(conflicting_booking)

    return booking


def create_booking(car, driver):
    '''
    Creates a new booking
    arguments
    - car: an existing car object
    - driver: the driver making the booking
    '''
    booking = Booking(car=car, driver=driver,)
    if booking.driver.documentation_approved:
        return request_insurance(booking)

    booking.save()
    ops_emails.new_booking_email(booking)
    return booking


def cancel(booking):
    if Booking.REQUESTED == booking.state:
        owner_emails.booking_canceled(booking)

    booking.state = Booking.CANCELED
    booking.incomplete_time = timezone.now()
    booking.incomplete_reason = Booking.REASON_CANCELED
    booking.save()

    ops_emails.booking_canceled(booking)
    driver_emails.booking_canceled(booking)
    return booking


def checkout(booking):
    # TODO - payment here
    booking.checkout_time = timezone.now()
    booking.save()
    # TODO - send some kind of confirmation message
    return booking


def pickup(booking):
    # TODO - payment here
    booking.state = Booking.BOOKED
    booking.pickup_time = timezone.now()
    booking.save()
    # TODO - send some kind of confirmation message
    return booking


def start_time_display(booking):
    def _format_date(date):
        return date.strftime('%b %d')

    if booking.pickup_time:
        return _format_date(booking.pickup_time)
    elif booking.approval_time:
        return 'on pickup'
    elif booking.checkout_time:
        return _format_date(booking.checkout_time + datetime.timedelta(days=2))
    else:
        return _format_date(timezone.now() + datetime.timedelta(days=2))


def min_rental_still_limiting(booking):
    min_notice = timezone.now() + datetime.timedelta(days=7)
    min_rental = car_service.get_min_rental_duration(booking.car)
    if not min_rental:
        return False

    if not booking.pickup_time or booking.pickup_time + datetime.timedelta(min_rental) > min_notice:
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
