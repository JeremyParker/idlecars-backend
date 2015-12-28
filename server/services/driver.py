# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime
from decimal import Decimal

from django.conf import settings
from django.utils import timezone
from django.db.models import Q

from credit import credit_service
from owner_crm.services import throttle_service, notification

import server.models
import server.services.booking
import server.services.experiment
from server.services import ServiceError


doc_fields_and_names = {
    'driver_license_image': 'your Drivers License',
    'fhv_license_image': 'your TLC License',
    'defensive_cert_image': 'your Defensive Driving certificate',
    'address_proof_image': 'a bill with your address on it',
}


def create(auth_user=None):
    return server.models.Driver.objects.create(auth_user=auth_user)


def documents_changed(original, modified):
    '''Returns True if any document had been changed between original driver and modified driver'''
    for doc in doc_fields_and_names.keys():
        if getattr(original, doc) != getattr(modified, doc):
            return True
    return False


def pre_save(modified_driver, orig):
    if documents_changed(orig, modified_driver):
        modified_driver.documentation_approved = False
        if modified_driver.all_docs_uploaded():
            notification.send('ops_notifications.DocumentsUploaded', modified_driver)

    if modified_driver.documentation_approved and not orig.documentation_approved:
        assign_credit_code(modified_driver)
        server.services.booking.on_docs_approved(modified_driver)

    return modified_driver


def post_save(modified_driver, orig):
    if modified_driver.base_letter and not orig.base_letter:
        server.services.booking.on_base_letter_approved(modified_driver)

    if modified_driver.base_letter_rejected and not orig.base_letter_rejected:
        #TODO: do something after driver fails to get base letter
        driver_notifications.base_letter_rejected(modified_driver)


def is_converted_driver(driver):
    return server.models.Payment.objects.filter(
        status=server.models.Payment.SETTLED,
        booking__driver=driver
    ).exists()


def assign_credit_code(driver):
    invitee, invitor = server.services.experiment.get_referral_rewards(driver)
    credit_service.create_invite_code(
        invitee_amount=invitee,
        invitor_amount=invitor,
        customer=driver.auth_user.customer,
    )


def assign_inactive_credit(driver):
    credit = server.services.experiment.get_inactive_credit(driver)
    customer = driver.auth_user.customer
    customer.app_credit += Decimal(credit)
    customer.save()
    return credit


def redeem_code(driver, code_string):
    # make sure the driver has never completed a booking
    if any(b.pickup_time for b in driver.booking_set.all()):
        raise ServiceError('Sorry, referral codes are for new drivers only.')
    try:
        credit_service.redeem_code(code_string, driver.auth_user.customer)
        notification.send('driver_notifications.SignupCredit', driver)
    except credit_service.CreditError as e:
        raise ServiceError(e.message)


def on_newly_converted(driver):
    # we tell the driver they can now invite their friends
    notification.send('driver_notifications.ReferFriends', driver)

    # whoever invited them gets app credit
    success, invitor_customer = credit_service.reward_invitor_for(driver.auth_user.customer)
    if success:
        server.services.experiment.referral_reward_converted(invitor_customer)
        try:
            invitor_driver = server.models.Driver.objects.get(auth_user__customer=invitor_customer)
            notification.send('driver_notifications.InvitorReceivedCredit', invitor_driver)
        except Exception:
            pass # we allow invitors who aren't drivers.


def on_set_email(driver):
    notification.send('driver_notifications.SignupConfirmation', driver)


def get_missing_docs(driver):
    ''' returns a list of the names of the driver's missing documents.'''
    missing = []
    for field, name in doc_fields_and_names.iteritems():
        if not getattr(driver, field):
            missing = missing + [name,]
    return missing


def get_default_payment_method(driver):
    return driver.paymentmethod_set.exclude(gateway_token='').order_by('pk').last()


def _get_remindable_drivers(delay_hours):
    reminder_threshold = timezone.now() - datetime.timedelta(hours=delay_hours)

    return server.models.Driver.objects.filter(
        documentation_approved=False,
        auth_user__date_joined__lte=reminder_threshold,
    ).filter(
        Q(driver_license_image__exact='') |
        Q(fhv_license_image__exact='') |
        Q(address_proof_image__exact='') |
        Q(defensive_cert_image__exact='')
    )


def _send_document_reminders(remindable_drivers, reminder_name, throttle_key):
    # send reminders to drivers who started an account, and never submitted docs
    throttled_drivers = throttle_service.throttle(remindable_drivers, throttle_key)
    for driver in throttled_drivers:
        # check each driver's pending bookings
        pending_bookings = server.services.booking.filter_pending(driver.booking_set)
        if pending_bookings:
            booking = pending_bookings.order_by('created_time').last()
            notification.send('driver_notifications.' + reminder_name + 'Booking', booking)
        else:
            notification.send('driver_notifications.' + reminder_name + 'Driver', driver)

    throttle_service.mark_sent(throttled_drivers, throttle_key)


def _inactive_coupon_reminder(delay_days):
    reminder_threshold = timezone.now() - datetime.timedelta(days=delay_days)
    remindable_drivers = server.models.Driver.objects.filter(
        auth_user__date_joined__lte=reminder_threshold,
    )
    throttled_drivers = throttle_service.throttle(remindable_drivers, 'InactiveCredit')
    skip_drivers = []
    for driver in throttled_drivers:
        if server.services.booking.processing_bookings(driver.booking_set):
            skip_drivers.append(driver.pk)
            continue

        credit = assign_inactive_credit(driver)
        notification.send('driver_notifications.InactiveCredit', driver, credit)
    throttle_service.mark_sent(throttled_drivers.exclude(pk__in=skip_drivers), 'InactiveCredit')


def _inactive_referral_reminder(delay_days):
    reminder_threshold = timezone.now() - datetime.timedelta(days=delay_days)
    remindable_drivers = server.models.Driver.objects.filter(
        auth_user__date_joined__lte=reminder_threshold,
        documentation_approved=True,
    )
    throttled_drivers = throttle_service.throttle(remindable_drivers, 'InactiveReferral')
    skip_drivers = []
    for driver in throttled_drivers:
        if server.services.booking.processing_bookings(driver.booking_set) or \
            is_converted_driver(driver):
            skip_drivers.append(driver.pk)
            continue

        notification.send('driver_notifications.InactiveReferral', driver)
    throttle_service.mark_sent(throttled_drivers.exclude(pk__in=skip_drivers), 'InactiveReferral')

def _credit_reminder(delay_days):
    '''
    Send a reminder to drivers who signed up with a credit code, but haven't spent
    the credit yet.
    '''
    reminder_threshold = timezone.now() - datetime.timedelta(days=delay_days)
    remindable_drivers = server.models.Driver.objects.filter(
        auth_user__date_joined__lte=reminder_threshold,
        auth_user__customer__invitor_code__isnull=False,
        auth_user__customer__invitor_credited=False,
    )
    throttled_drivers = throttle_service.throttle(remindable_drivers, 'UseYourCredit')
    skip_drivers = []
    for driver in throttled_drivers:
        if server.services.booking.processing_bookings(driver.booking_set):
            skip_drivers.append(driver.pk)
            continue

        notification.send('driver_notifications.UseYourCredit', driver)
    throttle_service.mark_sent(throttled_drivers.exclude(pk__in=skip_drivers), 'UseYourCredit')


def _signup_reminder(delay_days, reminder_name):
    reminder_threshold = timezone.now() - datetime.timedelta(days=delay_days)
    remindable_drivers = server.models.Driver.objects.filter(
        auth_user__date_joined__lte=reminder_threshold,
        braintree_customer_id__isnull=True,
    )
    throttled_drivers = throttle_service.throttle(remindable_drivers, reminder_name)
    skip_drivers = []
    for driver in throttled_drivers:
        if server.services.booking.post_pending_bookings(driver.booking_set):
            skip_drivers.append(driver.pk)
            continue

        notification.send('driver_notifications.'+reminder_name, driver)
    throttle_service.mark_sent(throttled_drivers.exclude(pk__in=skip_drivers), reminder_name)


def process_signup_notifications():
    _signup_reminder(
        delay_days=7,
        reminder_name='SignupFirstReminder',
    )
    _signup_reminder(
        delay_days=30,
        reminder_name='SignupSecondReminder',
    )


def process_credit_notifications():
    _credit_reminder(delay_days=14)
    _inactive_coupon_reminder(delay_days=14)


def process_referral_notifications():
    _inactive_referral_reminder(delay_days=21)


def process_document_notifications():
    _send_document_reminders(
      remindable_drivers=_get_remindable_drivers(1),
      reminder_name='FirstDocumentsReminder',
      throttle_key='first_documents_reminder',
    )
    _send_document_reminders(
      remindable_drivers=_get_remindable_drivers(24),
      reminder_name='SecondDocumentsReminder',
      throttle_key='second_documents_reminder',
    )
    _send_document_reminders(
      remindable_drivers=_get_remindable_drivers(36),
      reminder_name='ThirdDocumentsReminder',
      throttle_key='third_documents_reminder',
    )
