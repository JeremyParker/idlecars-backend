# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.core.urlresolvers import reverse
from django.utils import timezone

from owner_crm.services import ops_emails, driver_emails, owner_emails

from server.models import Booking, Payment
from . import payment as payment_service
from server.services import car as car_service
from server.payment_gateways import braintree_payments


def filter_pending(booking_queryset):
    return booking_queryset.filter(
        checkout_time__isnull=True,
        incomplete_time__isnull=True,
    )

def filter_reserved(booking_queryset):
    return booking_queryset.filter(
        checkout_time__isnull=False,
        requested_time__isnull=True,
        incomplete_time__isnull=True,
    )

def is_visible(booking):
    ''' Can this booking be seen in the Driver app '''
    return not booking.return_time and not booking.incomplete_time


def filter_visible(booking_queryset):
    ''' Can this booking be seen in the Driver app '''
    return booking_queryset.filter(return_time__isnull=True, incomplete_time__isnull=True)


def send_reminders():
    # send reminders to drivers who started booking a car, and never submitted docs
    docs_reminder_delay_hours = 1  # TODO(JP): get from config

    reminder_threshold = timezone.now() - datetime.timedelta(hours=docs_reminder_delay_hours)
    remindable_bookings = filter_pending(
        Booking.objects.filter(created_time__lte=reminder_threshold)
    )

    for booking in remindable_bookings:
        if not booking.driver.email():
            continue
        # TODO - send email and mark email sent
        # driver_emails.documents_reminder(booking)
        # booking.get_state = Booking.FLAKE
        # booking.save()


def on_documents_approved(driver):
    bookings = filter_reserved(Booking.objects.filter(driver=driver))
    if not bookings:
        driver_emails.documents_approved_no_booking(driver)
        return

    for booking in bookings:
        request_insurance(booking)


def someone_else_booked(booking):
    booking.incomplete_time = timezone.now()
    booking.incomplete_reason = Booking.REASON_ANOTHER_BOOKED
    booking.save()
    driver_emails.someone_else_booked(booking)
    return booking


def request_insurance(booking):
    owner_emails.new_booking_email(booking)
    booking.requested_time = timezone.now()
    booking.save()
    return booking


def create_booking(car, driver):
    '''
    Creates a new booking
    arguments
    - car: an existing car object
    - driver: the driver making the booking
    '''
    booking = Booking.objects.create(car=car, driver=driver,)
    ops_emails.new_booking_email(booking)
    return booking


def can_cancel(booking):
    return not booking.approval_time


def cancel(booking):
    if Booking.REQUESTED == booking.get_state():
        owner_emails.booking_canceled(booking)

    for payment in booking.payment_set.filter(status=Payment.PRE_AUTHORIZED):
        payment_service.void(payment)

    booking.incomplete_time = timezone.now()
    booking.incomplete_reason = Booking.REASON_CANCELED
    booking.save()

    ops_emails.booking_canceled(booking)
    driver_emails.booking_canceled(booking)
    return booking


def can_checkout(booking):
    # TODO - check that the car is still available (may have been a race to book)
    if not booking.driver.all_docs_uploaded():
        return False
    if booking.get_state() != Booking.PENDING:
        return False
    if not booking.driver.braintree_customer_id:
        return False
    if not booking.driver.paymentmethod_set.exists():
        return False
    return True


def _make_deposit_payment(booking):
    payment = payment_service.create_payment(
        booking,
        booking.car.solo_deposit,
    )
    payment = payment_service.pre_authorize(payment)
    return payment


def checkout(booking):
    if not can_checkout(booking):
        raise Exception("Booking cannot be checked out in its current state")

    payment = _make_deposit_payment(booking)
    # TODO - handle all the error cases

    if payment.status == Payment.PRE_AUTHORIZED:
        booking.checkout_time = timezone.now()
        booking.save()
        # TODO - send some kind of confirmation message

        # cancel other conflicting in-progress bookings and notify those drivers
        conflicting_pending_bookings = filter_pending(Booking.objects.filter(car=booking.car))
        for conflicting_booking in conflicting_pending_bookings:
            conflicting_booking = someone_else_booked(conflicting_booking)

        if booking.driver.documentation_approved:
            return request_insurance(booking)

    return booking


def can_pickup(booking):
    return booking.get_state() == Booking.ACCEPTED


def _find_deposit_payment(booking):
    try:
        deposit_payment = booking.payment_set.get(status=Payment.PRE_AUTHORIZED)
    except Payment.DoesNotExist:
        try:
            deposit_payment = booking.payment_set.get(status=Payment.SETTLED)
        except Payment.DoesNotExist:
            return None
    return deposit_payment


def pickup(booking):
    deposit_payment = _find_deposit_payment(booking) or _make_deposit_payment(booking)
    # TODO - error handling with message to the user

    # pre-authorize the payment for the first week's rent
    rent_payment = payment_service.create_payment(booking, booking.car.solo_cost)
    rent_payment = payment_service.pre_authorize(rent_payment)
    if rent_payment.status != Payment.PRE_AUTHORIZED:
        # TODO - error handling with message to the user
        return booking

    # hold the deposit in escrow for the duration of the rental
    if deposit_payment.status is not Payment.HELD_IN_ESCROW:
        deposit_payment = payment_service.escrow(deposit_payment)
    if deposit_payment.status != Payment.HELD_IN_ESCROW:
        # TODO - error handling with message to the user
        return booking

    # take payment for the first week's rent
    rent_payment = payment_service.settle(rent_payment)
    if rent_payment.status != Payment.SETTLED:
        # TODO - error handling with message to the user
        return booking

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
