# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

from owner_crm.services import message as message_service
from server.services import owner_service
from server.services import driver as driver_service


def throttle_all_overdue_emails(apps, schema_editor):
    # backfill the driver document reminder email records
    email_specs = [
        (1, 'first_documents_reminder'),
        (24, 'second_documents_reminder'),
        (36, 'third_documents_reminder'),
    ]
    for email_spec in email_specs:
        for driver in driver_service._get_remindable_drivers(delay_hours=email_spec[0]):
            message_service.log_message(email_spec[1], driver)

    # backfill the owner insurance reminder email records
    email_specs = [
        (12, 'first_morning_insurance_reminder'),
        (36, 'second_morning_insurance_reminder'),
        (12, 'first_afternoon_insurance_reminder'),
        (36, 'second_afternoon_insurance_reminder'),
    ]
    for email_spec in email_specs:
        bookings = owner_service._get_remindable_bookings(email_spec[0])
        for booking in bookings:
            message_service.log_message(email_spec[1], booking)


class Migration(migrations.Migration):
    dependencies = [
        ('server', '0068_merge'),
    ]

    operations = [
        migrations.RunPython(
            throttle_all_overdue_emails,
            reverse_code=migrations.RunPython.noop
        ),
    ]
