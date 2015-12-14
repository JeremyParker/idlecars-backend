# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from server.services import driver as driver_service


class Command(BaseCommand):
    help = 'Sends notifications to drivers'

    def handle(self, *args, **options):
        driver_service.process_driver_emails()

