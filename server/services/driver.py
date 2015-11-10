# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.utils import timezone
from django.db.models import Q

from owner_crm.models import ops_notifications, driver_notifications
from owner_crm.services import throttle_service, notification

import server.models
import server.services.booking


doc_fields_and_names = {
    'driver_license_image': 'your Drivers License',
    'fhv_license_image': 'your TLC License',
    'defensive_cert_image': 'your Defensive Driving certificate',
    'address_proof_image': 'a bill with your address on it',
}


def create():
    return server.models.Driver.objects.create()


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
        server.services.booking.on_docs_approved(modified_driver)

    return modified_driver


def post_save(modified_driver, orig):
    if modified_driver.base_letter and not orig.base_letter:
        server.services.booking.on_base_letter_approved(modified_driver)

    if modified_driver.base_letter_rejected and not orig.base_letter_rejected:
        #TODO: do something after driver fail to get base letter
        driver_notifications.base_letter_rejected(modified_driver)


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


def process_driver_emails():
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
