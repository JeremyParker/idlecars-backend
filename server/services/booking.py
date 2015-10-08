# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime
from decimal import Decimal, ROUND_UP

from django.core.urlresolvers import reverse
from django.db.models import F
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

def filter_booked(booking_queryset):
    return booking_queryset.filter(
        incomplete_time__isnull=True,
        refund_time__isnull=True,
        return_time__isnull=True,
        pickup_time__isnull=False,
    )

def is_visible(booking):
    ''' Can this booking be seen in the Driver app '''
    return not booking.return_time and not booking.incomplete_time


def filter_visible(booking_queryset):
    ''' Can this booking be seen in the Driver app '''
    return booking_queryset.filter(return_time__isnull=True, incomplete_time__isnull=True)


def on_base_letter_approved(driver):
    reserved_bookings = filter_reserved(Booking.objects.filter(driver=driver))
    pending_bookings = filter_pending(Booking.objects.filter(driver=driver))
    if not pending_bookings and not reserved_bookings:
        driver_emails.base_letter_approved_no_booking(driver)
        return

    for booking in pending_bookings:
        driver_emails.base_letter_approved_no_checkout(booking)

    for booking in reserved_bookings:
        request_insurance(booking)


def someone_else_booked(booking):
    booking.incomplete_time = timezone.now()
    booking.incomplete_reason = Booking.REASON_ANOTHER_BOOKED
    booking.save()
    driver_emails.someone_else_booked(booking)
    return booking


def request_insurance(booking):
    owner_emails.new_booking_email(booking)
    driver_emails.awaiting_insurance_email(booking)
    booking.requested_time = timezone.now()
    booking.save()
    return booking


def on_insurance_approved(booking):
    driver_emails.insurance_approved(booking)


def on_returned(booking):
    # TODO - issue a refund and email all parties
    pass


def on_incomplete(booking, reason):
    ''' Called when an admin sets a booking to incomplete'''
    if reason == Booking.REASON_OWNER_REJECTED:
        driver_emails.insurance_rejected(booking)
    elif reason == Booking.REASON_DRIVER_REJECTED:
        owner_emails.driver_rejected(booking)
    elif reason == Booking.REASON_MISSED:
        driver_emails.car_rented_elsewhere(booking)
    # NOTE: elsewhere we handle:
    # Booking.REASON_ANOTHER_BOOKED
    # Booking.REASON_CANCELED


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


def _make_deposit_payment(booking):
    payment = payment_service.create_payment(
        booking,
        booking.car.solo_deposit,
    )
    payment = payment_service.pre_authorize(payment)
    return payment


def _find_deposit_payment(booking):
    try:
        deposit_payment = booking.payment_set.get(status=Payment.PRE_AUTHORIZED)
    except Payment.DoesNotExist:
        try:
            deposit_payment = booking.payment_set.get(status=Payment.SETTLED)
        except Payment.DoesNotExist:
            return None
    return deposit_payment


def calculate_next_rent_payment(booking):
    if not booking.checkout_time:
        return (None, None, None, None)

    previous_payments = booking.payment_set.filter(
        invoice_start_time__isnull=False,
        invoice_end_time__isnull=False,
    ).order_by('invoice_end_time')

    if not previous_payments:  # first rent payment
        start_time = timezone.now().replace(microsecond=0)
    else:
        start_time = previous_payments.last().invoice_end_time

    end_time = start_time + datetime.timedelta(days=7)

    amount = booking.weekly_rent
    take_rate = booking.service_percentage

    booking_end_time = booking.end_time or calculate_end_time(booking)

    if booking_end_time < end_time:
        end_time = booking_end_time
        parital_week = amount * Decimal((booking_end_time - start_time).days) / Decimal(7.00)
        amount = parital_week.quantize(Decimal('.01'), rounding=ROUND_UP)
    return (
        Decimal(amount * take_rate).quantize(Decimal('.01'), rounding=ROUND_UP),
        amount,
        start_time,
        end_time
    )


def _create_next_rent_payment(booking):
    fee, amount, start_time, end_time = calculate_next_rent_payment(booking)

    return payment_service.create_payment(
        booking,
        amount,
        service_fee=fee,
        invoice_start_time=start_time,
        invoice_end_time=end_time,
    )


def can_checkout(booking):
    # TODO - check that the car is still available (may have been a race to book)
    # TODO - check the owner's bank creds are OK
    if not booking.driver.all_docs_uploaded():
        return False
    if booking.get_state() != Booking.PENDING:
        return False
    if not booking.driver.braintree_customer_id:
        return False
    if not booking.driver.paymentmethod_set.exists():
        return False
    return True


def checkout(booking):
    if not can_checkout(booking):
        raise Exception("Booking cannot be checked out in its current state")

    payment = _make_deposit_payment(booking)
    # TODO - handle all the error cases

    if payment.status == Payment.PRE_AUTHORIZED:
        booking.checkout_time = timezone.now()

        # lock-in pricing details by copying them to the booking
        booking.weekly_rent = booking.car.solo_cost
        booking.service_percentage = booking.car.owner.effective_service_percentage
        booking.save()
        # TODO - send some kind of confirmation message

        # cancel other conflicting in-progress bookings and notify those drivers
        conflicting_pending_bookings = filter_pending(Booking.objects.filter(car=booking.car))
        for conflicting_booking in conflicting_pending_bookings:
            conflicting_booking = someone_else_booked(conflicting_booking)

        if booking.driver.documentation_approved and booking.driver.base_letter:
            return request_insurance(booking)

        driver_emails.checkout_recipt(booking)

    return booking


def can_pickup(booking):
    return booking.get_state() == Booking.ACCEPTED


def pickup(booking):
    # NB: we don't save() the booking unless successful...
    booking.pickup_time = timezone.now()
    if not booking.end_time:
        booking.end_time = calculate_end_time(booking)

    deposit_payment = _find_deposit_payment(booking) or _make_deposit_payment(booking)
    # TODO - error handling with message to the user

    # pre-authorize the payment for the first week's rent
    rent_payment = _create_next_rent_payment(booking)
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

    # copy the time of day from the pickup time to the booking end time. Until now it had none.
    booking.end_time = booking.end_time.replace(
        hour=booking.pickup_time.hour,
        minute=booking.pickup_time.minute,
        second=booking.pickup_time.second,
    )

    booking.save()
    # TODO - send some kind of confirmation message
    return booking


def cron_payments():
    payment_lead_time_hours = 2  # TODO - get this out of a config system
    pay_time = timezone.now() + datetime.timedelta(hours=payment_lead_time_hours)
    payable_bookings = filter_booked(Booking.objects.all()).exclude(
        payment__invoice_end_time__isnull=False,
        payment__invoice_end_time__gt=pay_time,
    ).exclude(
        payment__invoice_end_time__isnull=False,
        payment__invoice_end_time__gte=F('end_time')
    )
    for booking in payable_bookings:
        try:
            payment = _create_next_rent_payment(booking)
            payment = payment_service.settle(payment)
        except Exception as e:
            print e
            ops_emails.payment_job_failed(booking, e)
            continue

        if not payment.status == Payment.SETTLED:
            ops_emails.payment_failed(payment)


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
    '''
    Is the minimum rental time still limiting the first first_valid_end_time, or is
    it the 7 days' notice?
    '''
    min_rental = booking.car.minimum_rental_days()
    if not min_rental:
        return False

    min_notice = timezone.now() + datetime.timedelta(days=7)
    if not booking.pickup_time or booking.pickup_time + datetime.timedelta(min_rental) > min_notice:
        return True
    return False


def first_valid_end_time(booking):
    '''
    Returns the earliest legal end time of the booking, so the user can't end the booking prematurely.
    '''
    if min_rental_still_limiting(booking):
        min_rental_days = booking.car.minimum_rental_days()
        return timezone.now() + datetime.timedelta(days=min_rental_days)
    return timezone.now() + datetime.timedelta(days=7)


def calculate_end_time(booking):
    assert not booking.end_time
    min_duration = booking.car.minimum_rental_days() or 1
    if booking.pickup_time:
        return booking.pickup_time + datetime.timedelta(days=min_duration)
    if booking.approval_time:
        return booking.approval_time + datetime.timedelta(days=min_duration + 1)
    elif booking.checkout_time:
        return booking.checkout_time + datetime.timedelta(days=min_duration + 2)
    else:
        return timezone.now() + datetime.timedelta(days=min_duration + 2)


def set_end_time(booking, end_time):
    if booking.end_time:
        booking.end_time = booking.end_time.replace(
            year=end_time.year,
            month=end_time.month,
            day=end_time.day,
        )
    else:
        booking.end_time = end_time

    booking.save()
    return booking
