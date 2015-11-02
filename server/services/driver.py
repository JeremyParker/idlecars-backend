# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.utils import timezone

from owner_crm.services import ops_notifications, driver_notifications
from owner_crm.services import throttle_service

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
            ops_notifications.documents_uploaded(modified_driver)

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
    )


def _send_document_reminders(docs_reminder_delay_hours, reminder_name):
    # send reminders to drivers who started an account, and never submitted docs
    remindable_drivers = _get_remindable_drivers(docs_reminder_delay_hours)
    throttle_service.send_to_queryset(remindable_drivers, eval('driver_notifications.' + reminder_name))


def process_driver_emails():
    _send_document_reminders(
      docs_reminder_delay_hours=1,
      reminder_name='first_documents_reminder'
    )
    _send_document_reminders(
      docs_reminder_delay_hours=24,
      reminder_name='second_documents_reminder'
    )
    _send_document_reminders(
      docs_reminder_delay_hours=36,
      reminder_name='third_documents_reminder'
    )
