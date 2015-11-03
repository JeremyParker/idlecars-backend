# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime
from decimal import Decimal, ROUND_UP

from django.core.urlresolvers import reverse
from django.db.models import F, Q
from django.utils import timezone
from django.conf import settings

from owner_crm.services import ops_notifications, driver_notifications, owner_notifications, street_team_notifications, notification

from server.models import Booking, Payment
from . import payment as payment_service
from server.services import car as car_service
from server.payment_gateways import braintree_payments


class BookingError(Exception):
    pass

CANCEL_ERROR = 'Sorry, your rental can\'t be canceled at this time. Please call Idlecars at ' + settings.IDLECARS_PHONE_NUMBER
PICKUP_ERROR = 'Sorry, your rental can\'t be picked up at this time.'
CHECKOUT_ERROR = 'Sorry, your rental can\'t be checked out at this time'
UNAVAILABLE_CAR_ERROR = 'Sorry, that car is unavailable right now. Here are other cars you can rent.'


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

def filter_requested(booking_queryset):
    return booking_queryset.filter(
        requested_time__isnull=False,
        approval_time__isnull=True,
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


def on_docs_approved(driver):
    if not driver.base_letter:
        bookings = Booking.objects.filter(driver=driver)

        if bookings:
            latest_booking = bookings.order_by('created_time').last()
            notification.send('street_team_notifications.RequestBaseLetter', latest_booking)
        else:
            notification.send('driver_notifications.DocsApprovedNoBooking', driver)


def on_base_letter_approved(driver):
    reserved_bookings = filter_reserved(Booking.objects.filter(driver=driver))
    pending_bookings = filter_pending(Booking.objects.filter(driver=driver))

    for booking in pending_bookings:
        driver_notifications.base_letter_approved_no_checkout(booking)

    for booking in reserved_bookings:
        request_insurance(booking)


def someone_else_booked(booking):
    return _make_booking_incomplete(booking, Booking.REASON_ANOTHER_BOOKED)


def request_insurance(booking):
    owner_notifications.new_booking_email(booking)
    driver_notifications.awaiting_insurance_email(booking)
    booking.requested_time = timezone.now()
    booking.save()
    return booking


def on_insurance_approved(booking):
    driver_notifications.insurance_approved(booking)


def on_returned(booking):
    # TODO - issue a refund and email all parties
    pass


def create_booking(car, driver):
    '''
    Creates a new booking
    arguments
    - car: an existing car object
    - driver: the driver making the booking
    '''
    booking = Booking.objects.create(car=car, driver=driver,)
    if booking.driver.documentation_approved and not booking.driver.base_letter:
        notification.send('street_team_notifications.RequestBaseLetter', booking)
    return booking


def can_cancel(booking):
    return not booking.approval_time


def cancel(booking):
    if not can_cancel(booking):
        raise BookingError(CANCEL_ERROR)
    _make_booking_incomplete(booking, Booking.REASON_CANCELED)


def _make_booking_incomplete(booking, reason):
    original_booking_state = booking.get_state()
    booking.incomplete_time = timezone.now()
    booking.incomplete_reason = reason
    booking.save()
    on_incomplete(booking, original_booking_state)
    return booking


def on_incomplete(booking, original_booking_state):
    ''' Called any time a booking is set to incomplete'''
    _void_all_payments(booking)

    # let our customers know what happened
    reason = booking.incomplete_reason
    if reason == Booking.REASON_CANCELED:
        driver_notifications.booking_canceled(booking)
        if Booking.REQUESTED == original_booking_state:
            owner_notifications.booking_canceled(booking)
    elif reason == Booking.REASON_OWNER_TOO_SLOW:
        owner_notifications.insurance_too_slow(booking)
        driver_notifications.insurance_failed(booking)
    elif reason == Booking.REASON_DRIVER_TOO_SLOW:
        driver_notifications.flake_reminder(booking.driver)
    elif reason == Booking.REASON_ANOTHER_BOOKED:
        driver_notifications.someone_else_booked(booking)
    elif reason == Booking.REASON_OWNER_REJECTED:
        driver_notifications.insurance_rejected(booking)
    elif reason == Booking.REASON_DRIVER_REJECTED:
        owner_notifications.driver_rejected(booking)
    elif reason == Booking.REASON_MISSED:
        driver_notifications.car_rented_elsewhere(booking)


def _make_deposit_payment(booking):
    payment = payment_service.create_payment(
        booking,
        booking.car.solo_deposit,
    )
    payment = payment_service.pre_authorize(payment)
    return payment


def _void_all_payments(booking):
    for payment in booking.payment_set.filter(status=Payment.PRE_AUTHORIZED):
        payment_service.void(payment)
        if payment.error_message:
            raise BookingError(payment.error_message)


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


def estimate_next_rent_payment(booking):
    '''
    Returns a tuple of (service_fee, rent_amount, start_time, end_time), based on
    an estimated pickup time
    '''
    assert not booking.pickup_time
    if not booking.checkout_time:
        return (None, None, None, None)

    estimated_pickup_time = estimate_pickup_time(booking)
    estimated_end_time = calculate_end_time(booking, estimated_pickup_time)
    return calculate_next_rent_payment(booking, estimated_pickup_time, estimated_end_time)


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

    return (
        service_fee,
        amount,
        invoice_start_time,
        invoice_end_time
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
        raise BookingError(CHECKOUT_ERROR)

    payment = _make_deposit_payment(booking)
    if payment.error_message:
        raise BookingError(payment.error_message)

    if payment.status == Payment.PRE_AUTHORIZED:
        booking.checkout_time = timezone.now()

        # lock-in pricing details by copying them to the booking
        booking.weekly_rent = booking.car.solo_cost
        booking.service_percentage = booking.car.owner.effective_service_percentage
        booking.save()

        # cancel other conflicting in-progress bookings and notify those drivers
        conflicting_pending_bookings = filter_pending(Booking.objects.filter(car=booking.car))
        for conflicting_booking in conflicting_pending_bookings:
            conflicting_booking = someone_else_booked(conflicting_booking)

        if booking.driver.documentation_approved and booking.driver.base_letter:
            return request_insurance(booking)

        driver_notifications.checkout_receipt(booking)

    return booking


def can_pickup(booking):
    return booking.get_state() == Booking.ACCEPTED


def pickup(booking):
    '''
    Warning: this method might change the booking even if it's unsuccessful. Caller should
    reload the object before relying on its data.
    '''
    if not can_pickup(booking):
        raise BookingError(PICKUP_ERROR)

    # NB: we don't save() the booking unless successful...
    booking.pickup_time = timezone.now().replace(microsecond=0)
    booking.end_time = calculate_end_time(booking, booking.pickup_time)

    deposit_payment = find_deposit_payment(booking) or _make_deposit_payment(booking)
    if deposit_payment.error_message:
        raise BookingError(deposit_payment.error_message)

    # pre-authorize the payment for the first week's rent
    rent_payment = _create_next_rent_payment(booking)
    rent_payment = payment_service.pre_authorize(rent_payment)
    if rent_payment.status != Payment.PRE_AUTHORIZED:
        raise BookingError(rent_payment.error_message)

    # hold the deposit in escrow for the duration of the rental
    if deposit_payment.status is not Payment.HELD_IN_ESCROW:
        deposit_payment = payment_service.escrow(deposit_payment)
    if deposit_payment.status != Payment.HELD_IN_ESCROW:
        raise BookingError(deposit_payment.error_message)

    # take payment for the first week's rent
    rent_payment = payment_service.settle(rent_payment)
    if rent_payment.status != Payment.SETTLED:
        raise BookingError(rent_payment.error_message)

    booking.save()

    driver_notifications.pickup_confirmation(booking)
    owner_notifications.pickup_confirmation(booking)

    return booking


def _cron_payments():
    payment_lead_time_hours = 2  # TODO - get this out of a config system
    pay_time = timezone.now() + datetime.timedelta(hours=payment_lead_time_hours)
    active_bookings = filter_booked(Booking.objects.all()).prefetch_related('payment_set')
    for booking in active_bookings:
        relevant_end_time = min(booking.end_time, pay_time)
        existing_payments = booking.payment_set.filter(
            invoice_end_time__isnull=False,
            invoice_end_time__gte=relevant_end_time,
            status=Payment.SETTLED,
        )
        if existing_payments.exists():
            continue

        # check if we failed wihtin that past 4 hours. If so, skip for now.
        if booking.payment_set.filter(
            invoice_end_time__isnull=False,
            invoice_end_time__gte=relevant_end_time,
            status=Payment.DECLINED,
            created_time__gte=timezone.now() - datetime.timedelta(hours=8)
        ):
            continue

        try:
            payment = _create_next_rent_payment(booking)
            payment = payment_service.settle(payment)
            if payment.error_message:
                print payment.error_message
                print payment.notes
                continue
            driver_notifications.payment_receipt(payment)
            owner_notifications.payment_receipt(payment)
        except Exception as e:
            print e
            ops_notifications.payment_job_failed(booking, e)


def _booking_updates():
    ''' Update the state of bookings based on the passing of time '''
    expired_bookings = filter_pending(Booking.objects.all()).filter(
        created_time__lte=timezone.now() - datetime.timedelta(hours=48), # TODO: from config
        driver__documentation_approved=False,  # TODO: filter out all the completed docs here
    )
    for booking in expired_bookings:
        try:
            if not booking.driver.all_docs_uploaded():
                _make_booking_incomplete(booking, Booking.REASON_DRIVER_TOO_SLOW)
        except BookingError:
            pass  # TODO: ops will get an email about the payment failure, and

    # TEMPORARILY REMOVING THIS FUNCTIONALITY. WE CAN SET OWNER TOO SLOW IN THE ADMIN NOW.
    # expired_bookings = filter_requested(Booking.objects.all()).filter(
    #     requested_time__lte=timezone.now() - datetime.timedelta(hours=60), # TODO: from config
    # )
    # for booking in expired_bookings:
    #     try:
    #         _make_booking_incomplete(booking, Booking.REASON_OWNER_TOO_SLOW)
    #     except BookingError:
    #         pass  # ops will get an email about the payment failure, and


def cron_job():
    _booking_updates()
    _cron_payments()


def start_time_display(booking):
    def _format_date(date):
        return date.strftime('%b %d')

    if booking.pickup_time:
        return _format_date(booking.pickup_time)
    elif booking.approval_time:
        return 'on pickup'
    else:
        return _format_date(estimate_pickup_time(booking))


def first_valid_end_time(booking):
    '''
    Returns a typle (ealiest legal end time, if the min_rental was limiting the 1st value)
    '''
    notice = timezone.now() + datetime.timedelta(days=7)
    min_rental = datetime.timedelta(days=booking.car.minimum_rental_days())
    min_rental_end = booking.pickup_time or estimate_pickup_time(booking) + min_rental
    return max(notice, min_rental_end), min_rental_end > notice


def estimate_pickup_time(booking):
    assert not booking.pickup_time  # if there's a pickup_time, then start_time is known.
    if booking.approval_time:
        pickup_date = booking.approval_time + datetime.timedelta(days=1)
    elif booking.checkout_time:
        pickup_date = booking.checkout_time + datetime.timedelta(days=2)
    else:
        pickup_date = timezone.now() + datetime.timedelta(days=2)

    now = timezone.now()
    pickup_time = pickup_date.replace(hour=now.hour, minute=now.minute, second=now.second)
    return pickup_time


def estimate_end_time(booking):
    assert not booking.pickup_time
    return calculate_end_time(booking, estimate_pickup_time(booking))


def calculate_end_time(booking, pickup_time):
    ''' calculate the end_time based on pickup_time. '''
    if booking.end_time:
        # booking.end_time may have been set through the API. If so, it had no time of day.
        return booking.end_time.replace(
            hour=pickup_time.hour,
            minute=pickup_time.minute,
            second=pickup_time.second,
        )
    else:
        min_duration = booking.car.minimum_rental_days() or 1
        return pickup_time + datetime.timedelta(days=min_duration)


# TODO: move this up to the API
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
