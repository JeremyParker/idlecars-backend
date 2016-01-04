# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import braintree
import random
import string
import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q

from owner_crm.services import password_reset_service, throttle_service, notification
from owner_crm.models import driver_notifications, owner_notifications, ops_notifications, OnboardingOwner

from server.models import Booking, Owner
from server.services import auth_user as auth_user_service
from server.services import car as car_service
from server.services import  booking as booking_service
from server import payment_gateways

#TODO: poke_frequency should be from setting, or config
POKE_FREQUENCY = 60 #minutes

STALENESS_WARNING_HOURS = 2 # we let owners know a few hours before their cars are stale


def _onboarding_reminder(delay_days, reminder_name):
    reminder_threshold = timezone.now() - datetime.timedelta(days=delay_days)
    remindable_owners = OnboardingOwner.objects.filter(created_time__lte=reminder_threshold)

    throttled_owners = throttle_service.throttle(remindable_owners, reminder_name)
    for owner in throttled_owners:
        notification.send('owner_notifications.'+reminder_name, owner)
    throttle_service.mark_sent(throttled_owners, reminder_name)


def _remove_converted_owners():
    pass


def process_onboarding_reminder():
    _onboarding_reminder(delay_days=0, reminder_name='FirstOnboardingReminder')


def _renewable_cars():
    return car_service.get_stale_within(
        minutes_until_stale=60 * STALENESS_WARNING_HOURS,
    )


def filter_incomplete(queryset):
    return queryset.filter(
        Q(zipcode='') |
        Q(merchant_id='')
    )


def process_renewal_reminder():
    throttle_key = 'RenewalEmail'
    throttled_renewable_cars = throttle_service.throttle(
        _renewable_cars(),
        throttle_key,
        hours=STALENESS_WARNING_HOURS + 1, # by this time cars will be renewed or stale
    )
    for car in throttled_renewable_cars:
        notification.send('owner_notifications.RenewalEmail', car)
    throttle_service.mark_sent(throttled_renewable_cars, throttle_key)


def _within_minutes_of_local_time(minutes, target_time):
    timedelta = datetime.timedelta(minutes=minutes)
    return target_time - timedelta < timezone.now() < target_time + timedelta


def _get_remindable_bookings(delay_hours):
    ''' returns booking queryset that were requested more than delay_hours ago '''
    reminder_threshold = timezone.now() - datetime.timedelta(hours=delay_hours)
    return booking_service.filter_requested(Booking.objects.all()).filter(
        requested_time__lte=reminder_threshold,
    )


def _send_reminder_email(remindable_bookings, reminder_name, throttle_key):
    throttled_bookings = throttle_service.throttle(remindable_bookings, throttle_key)

    campaign_name = 'owner_notifications.' + reminder_name
    for booking in throttled_bookings:
        notification.send(campaign_name, booking)

    throttle_service.mark_sent(throttled_bookings, throttle_key)


def process_pending_booking_reminder():
    reminder_threshold = timezone.now() - datetime.timedelta(hours=24)
    remindable_bookings = booking_service.filter_pending(Booking.objects.all()).filter(
        created_time__lte=reminder_threshold,
        driver__paymentmethod__isnull=True,
    )
    throttled_bookings = throttle_service.throttle(remindable_bookings, 'PendingNotification')
    for booking in throttled_bookings:
        notification.send('owner_notifications.PendingNotification', booking)
    throttle_service.mark_sent(throttled_bookings, 'PendingNotification')


def process_insurance_reminder():
    # TODO: hour, minute and delay_hours should be from settings
    morning_target = timezone.localtime(timezone.now()).replace(hour=10, minute=0)
    afternoon_target = timezone.localtime(timezone.now()).replace(hour=17, minute=0)
    delay_hours = 12

    if _within_minutes_of_local_time(POKE_FREQUENCY/2, morning_target):

        _send_reminder_email(
            remindable_bookings=_get_remindable_bookings(delay_hours=delay_hours),
            reminder_name='FirstMorningInsuranceReminder',
            throttle_key='first_morning_insurance_reminder',
        )
        _send_reminder_email(
            remindable_bookings=_get_remindable_bookings(delay_hours=delay_hours + 24),
            reminder_name='SecondMorningInsuranceReminder',
            throttle_key='second_morning_insurance_reminder',
        )

    elif _within_minutes_of_local_time(POKE_FREQUENCY/2, afternoon_target):
        _send_reminder_email(
            remindable_bookings=_get_remindable_bookings(delay_hours=delay_hours),
            reminder_name='FirstAfternoonInsuranceReminder',
            throttle_key='first_afternoon_insurance_reminder',
        )
        _send_reminder_email(
            remindable_bookings=_get_remindable_bookings(delay_hours=delay_hours + 24),
            reminder_name='SecondAfternoonInsuranceReminder',
            throttle_key='second_afternoon_insurance_reminder',
        )

def _account_reminder(delay_hours, reminder_name):
    reminder_threshold = timezone.now() - datetime.timedelta(hours=delay_hours)
    remindable_owners = filter_incomplete(Owner.objects.all()).filter(
        auth_users__date_joined__lte=reminder_threshold,
        cars__isnull=False,
    )
    throttled_owners = throttle_service.throttle(remindable_owners, reminder_name)
    for owner in throttled_owners:
        notification.send('owner_notifications.'+reminder_name, owner)
    throttle_service.mark_sent(throttled_owners, reminder_name)


def process_account_reminder():
    _account_reminder(delay_hours=24, reminder_name='FirstAccountReminder')
    _account_reminder(delay_hours=48, reminder_name='SecondAccountReminder')


def create(auth_user):
    new_owner = Owner.objects.create()
    new_owner.auth_users.add(auth_user)
    return new_owner


def on_set_email(owner):
    notification.send('owner_notifications.SignupConfirmation', owner)


def add_merchant_id_to_owner(merchant_account_id, owner):
    owner.merchant_id = merchant_account_id
    owner.merchant_account_state = Owner.BANK_ACCOUNT_PENDING
    return owner.save()


def update_account_state(merchant_account_id, state, errors=None):
    owner = Owner.objects.get(merchant_id=merchant_account_id)
    owner.merchant_account_state = state
    owner.save()

    if owner.merchant_account_state is Owner.BANK_ACCOUNT_APPROVED:
        notification.send('owner_notifications.BankAccountApproved', owner)
    else:
        notification.send('ops_notifications.OwnerAccountDeclined', owner, errors)


def _strip_dict(dictionary, valid_schema):
    valid_keys = valid_schema.keys()
    invalid_keys = []
    for (k, v) in dictionary.iteritems():
        if not k in valid_keys:
            invalid_keys.append(k)
        elif isinstance(v, dict):
            dictionary.update({ k: _strip_dict(v, valid_schema[k]) })
    for k in invalid_keys:
        del(dictionary[k])
    return dictionary


def link_bank_account(owner, params):
    #translate client params into the format Braintree expects.
    try:
        params['individual']['phone'] = params['individual']['phone_number']
        params['individual'].pop("phone_number", None)
    except KeyError:
        return [], ['Sorry, something went wrong there. Please try again.']

    # This is a superset of all the keys we can pass to braintree
    valid_schema = {
        'funding': {
            'account_number': None,
            'routing_number': None,
        },
        'business': {
            'legal_name': None,
            'tax_id': None,
        },
        'individual': {
            'address': {
                'locality': None,
                'postal_code': None,
                'region': None,
                'street_address': None,
            },
            'date_of_birth': None,
            'email': None,
            'first_name': None,
            'last_name': None,
            'phone': None,
        },
        "tos_accepted": None,
    }

    _strip_dict(params, valid_schema)

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
