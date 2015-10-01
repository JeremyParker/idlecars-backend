# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from server.services import driver as driver_service


class Command(BaseCommand):
    help = 'Sends notifications to drivers'

    def handle(self, *args, **options):
        driver_service.send_document_reminders(docs_reminder_delay_hours=1, reminder_name='first_documents_reminder')
        driver_service.send_document_reminders(docs_reminder_delay_hours=24, reminder_name='second_documents_reminder')
        driver_service.send_document_reminders(docs_reminder_delay_hours=36, reminder_name='third_documents_reminder')

        driver_service.send_flake_reminders(flake_reminder_delay_hours=48)
