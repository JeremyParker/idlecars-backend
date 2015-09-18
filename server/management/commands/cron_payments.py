# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from server.services import booking as booking_service


class Command(BaseCommand):
    help = 'Checks if its time to make any payments, and makes payments if necessary'

    def handle(self, *args, **options):
        booking_service.cron_payments()
