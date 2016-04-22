# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from server.services import owner_service

class Command(BaseCommand):
    help = 'Sends notifications to owners about the state of their cars'

    def handle(self, *args, **options):
        owner_service.process_renewal_reminder()
        # owner_service.process_insurance_reminder()
