# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from server import models as server_models
from crm.services import driver_emails


class Command(BaseCommand):
    help = 'Sends notifications to drivers'

    def handle(self, *args, **options):
        # send reminders to drivers who started booking a car, and never submitted docs
        for booking in self.remindable_bookings():
            driver_emails.documents_reminder(booking)
            booking.state = server_models.Booking.FLAKE
            booking.save()

    def remindable_bookings(self):
        docs_reminder_delay_hours = 24  # TODO(JP): get from config

        reminder_threshold = timezone.now() - datetime.timedelta(hours=docs_reminder_delay_hours)
        return server_models.Booking.objects.filter(
            state=server_models.Booking.PENDING,
            created_time__lte=reminder_threshold,
        )
