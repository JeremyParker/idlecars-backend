# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import braintree
import random
import string
import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone

from owner_crm.services import password_reset_service, driver_emails, owner_emails, ops_emails, throttle_service
from owner_crm.models import Renewal

from server.models import Booking, Owner, UserAccount

from server.services import auth_user as auth_user_service
from server.services import car as car_service
from server import payment_gateways


def _renewable_cars():
    # TODO - optimize this query
    oustanding_renewal_cars = [r.car.id for r in Renewal.objects.filter(state=Renewal.STATE_PENDING)]
    return car_service.get_stale_within(
        minutes_until_stale=60 * 2,
    ).exclude(
        id__in = oustanding_renewal_cars,
    )


def _renewal_email():
    for car in _renewable_cars():
        renewal = Renewal.objects.create(car=car)
        owner_emails.renewal_email(car=car, renewal=renewal)


def _in_time(threshold):
    #TODO: poke_frequency should be from setting
    poke_frequency = 15 #minutes
    timedelta = datetime.timedelta(minutes=poke_frequency)/2
    return threshold - timedelta < datetime.datetime.now() < threshold + timedelta


def _get_remindable_bookings(delay_hours):
    reminder_threshold = timezone.now() - datetime.timedelta(hours=delay_hours)

    return Booking.objects.filter(
        requested_time__lte=reminder_threshold,
        checkout_time__isnull=False,
        requested_time__isnull=False,
        approval_time__isnull=True,
        incomplete_time__isnull=True,
    )


def _send_reminder_email(insurance_reminder_delay_hours, reminder_name):
    remindable_bookings = _get_remindable_bookings(insurance_reminder_delay_hours)
    throttle_service.send_to_queryset(remindable_bookings, eval('owner_emails.' + reminder_name))


def _send_too_slow_email(too_slow_reminder_delay_hours):
    remindable_bookings = _get_remindable_bookings(too_slow_reminder_delay_hours)
    throttle_service.send_to_queryset(remindable_bookings, owner_emails.insurance_too_slow)
    throttle_service.send_to_queryset(remindable_bookings, driver_emails.insurance_failed)

    for booking in remindable_bookings:
        booking.incomplete_time = timezone.now()
        booking.incomplete_reason = Booking.REASON_INSURANCE_TOO_SLOW
        booking.save()


def _reminder_email():
    #TODO: hour, minute and delay_hours should be from settings
    morning_threshold = datetime.datetime.now().replace(hour=10, minute=0)
    afternoon_threshold = datetime.datetime.now().replace(hour=17, minute=0)

    delay_hours = 12

    if _in_time(morning_threshold):
        _send_reminder_email(
            insurance_reminder_delay_hours=delay_hours,
            reminder_name='first_morning_insurance_reminder'
        )
        _send_reminder_email(
            insurance_reminder_delay_hours=delay_hours+24,
            reminder_name='second_morning_insurance_reminder'
        )
        _send_too_slow_email(delay_hours+48)

    elif _in_time(afternoon_threshold):
        _send_reminder_email(
            insurance_reminder_delay_hours=delay_hours,
            reminder_name='first_afternoon_insurance_reminder'
        )
        _send_reminder_email(
            insurance_reminder_delay_hours=delay_hours+24,
            reminder_name='second_afternoon_insurance_reminder'
        )
        _send_too_slow_email(delay_hours+48)


def process_owner_emails():
    _renewal_email()
    _reminder_email()


def add_merchant_id_to_owner(merchant_account_id, owner):
    owner.merchant_id = merchant_account_id
    owner.merchant_account_state = Owner.BANK_ACCOUNT_PENDING
    return owner.save()


def update_account_state(merchant_account_id, state, errors=None):
    owner = Owner.objects.get(merchant_id=merchant_account_id)
    owner.merchant_account_state = state
    owner.save()

    if owner.merchant_account_state is Owner.BANK_ACCOUNT_APPROVED:
        owner_emails.bank_account_approved(owner)
    else:
        ops_emails.owner_account_declined(owner, errors)

def link_bank_account(owner, params):
    #translate client params into the format Braintree expects.
    try:
        params['individual']['phone'] = params['individual']['phone_number']
        params['individual'].pop("phone_number", None)
    except KeyError:
        return [], ['Sorry, something went wrong there. Please try again.']

    gateway = payment_gateways.get_gateway(settings.PAYMENT_GATEWAY_NAME)
    success, merchant_account_id, error_fields, error_msg = gateway.link_bank_account(params)
    if success:
        add_merchant_id_to_owner(merchant_account_id, owner)
        return [], []
    else:
        return error_fields, error_msg


def invite_legacy_owner(phone_number):
    '''
    emails that User to reset their password, and link their bank account.
    Raises Owner.DoesNotExist if there wasn't an owner account for this number
    args:
    - phone_number: phone number of the user. Must contain no non-digit characters.
    '''
    try:
        auth_user = User.objects.get(username=phone_number)
    except User.DoesNotExist:
        raise Owner.DoesNotExist
    owner = Owner.objects.get(auth_users=auth_user)
    password_reset_service.invite_owner(auth_user)
    return auth_user
