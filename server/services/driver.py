# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.utils import timezone

from owner_crm.services import ops_emails, driver_emails
from owner_crm.services import campaign as campaign_service

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


def pre_save(modified_driver):
    if modified_driver.pk is not None:
        orig = server.models.Driver.objects.get(pk=modified_driver.pk)
        if documents_changed(orig, modified_driver):
            modified_driver.documentation_approved = False
            if modified_driver.all_docs_uploaded():
                ops_emails.documents_uploaded(modified_driver)
                server.services.booking.on_documents_uploaded(modified_driver)
                # TODO(JP): maybe send a welcome email to the Driver immediately?

        if modified_driver.documentation_approved and not orig.documentation_approved:
            server.services.booking.on_documents_approved(modified_driver)

    return modified_driver


def get_missing_docs(driver):
    ''' returns a list of the names of the driver's missing documents.'''
    missing = []
    for field, name in doc_fields_and_names.iteritems():
        if not getattr(driver, field):
            missing = missing + [name,]
    return missing


def send_reminders():
    # send reminders to drivers who started an account, and never submitted docs
    docs_reminder_delay_hours = 1  # TODO(JP): get from config

    reminder_threshold = timezone.now() - datetime.timedelta(hours=docs_reminder_delay_hours)
    remindable_drivers = server.models.Driver.objects.filter(
        documentation_approved=False,
        auth_user__date_joined__lte=reminder_threshold,
    )
    campaign_service.send_to_queryset(remindable_drivers, driver_emails.documents_reminder)
