# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from idlecars import email
from owner_crm.services import password_reset_service
from owner_crm.models import driver_notifications

class Command(BaseCommand):
    help = '''
    This command will start the password rest process manually for a given user.
    args
    - phone_number: the phone number for the user to send an invite to.
    '''

    def add_arguments(self, parser):
        parser.add_argument('phone_numbers', nargs='+', type=str)

    def handle(self, *args, **options):
        phone_numbers = options['phone_numbers']
        for phone_number in phone_numbers:
            password_reset = password_reset_service.create(phone_number)
            if password_reset:
                driver_notifications.password_reset(password_reset)
                self.stdout.write('Password reset email sent for {}'.format(phone_number))
            else:
                self.stdout.write('ERROR resetting password for {}'.format(phone_number))
