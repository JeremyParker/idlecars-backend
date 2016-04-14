# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime
from decimal import Decimal, ROUND_UP

from django.utils import timezone

from owner_crm.services import notification

from server.models import Payment, Booking
from server.services import payment as payment_service
from server.services import ServiceError


def void_all_payments(booking):
    for payment in booking.payment_set.filter(status=Payment.PRE_AUTHORIZED):
        payment_service.void(payment)
        if payment.error_message:
            raise ServiceError(payment.error_message)


def make_deposit_payment(booking):
    payment = payment_service.create_payment(
        booking,
        booking.car.deposit,
    )
    payment = payment_service.pre_authorize(payment)
    return payment


def find_deposit_payment(booking):
    potential_deposits = booking.payment_set.filter(
            invoice_start_time__isnull=True,
            invoice_end_time__isnull=True,
        )
    try:
        deposit_payment = potential_deposits.get(status=Payment.PRE_AUTHORIZED)
    except Payment.DoesNotExist:
        try:
            deposit_payment = potential_deposits.get(status=Payment.HELD_IN_ESCROW)
        except Payment.DoesNotExist:
            return None
    return deposit_payment


def calculate_next_rent_payment(booking, booking_pickup_time=None, booking_end_time=None):
    '''
    Returns a tuple of (service_fee, rent_amount, start_time, end_time).
    pickup_time and end_time may be used to override the booking's values, or
    for estimation if booking's values aren't set yet.
    '''
    assert booking_pickup_time or booking.pickup_time
    assert booking_end_time or booking.end_time

    previous_payments = booking.payment_set.filter(
        invoice_start_time__isnull=False,
        invoice_end_time__isnull=False,
        status=Payment.SETTLED,
    ).order_by('invoice_end_time')

    if previous_payments:
        invoice_start_time = previous_payments.last().invoice_end_time
    else:
        invoice_start_time = booking_pickup_time or booking.pickup_time

    invoice_end_time = min(
        invoice_start_time + datetime.timedelta(days=7),
        booking_end_time or booking.end_time,
    )

    week_portion = Decimal((invoice_end_time - invoice_start_time).days) / Decimal(7.00)
    amount = (
        week_portion * booking.weekly_rent).quantize(Decimal('.01'),
        rounding=ROUND_UP
    )
    service_fee = Decimal(
        amount * booking.service_percentage).quantize(Decimal('.01'),
        rounding=ROUND_UP
    )

    # user some credit if the customer has any app credit
    customer = booking.driver.auth_user.customer
    cash_amount = max(Decimal('0.00'), amount - customer.app_credit)
    credit_amount = amount - cash_amount

    return (
        service_fee,
        cash_amount,
        credit_amount,
        invoice_start_time,
        invoice_end_time
    )


def create_next_rent_payment(booking):
    # invoice the driver
    fee, cash_amount, credit_amount, start_time, end_time = calculate_next_rent_payment(booking)
    return payment_service.create_payment(
        booking,
        cash_amount,
        credit_amount,
        service_fee=fee,
        invoice_start_time=start_time,
        invoice_end_time=end_time,
    )
