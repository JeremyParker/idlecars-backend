# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from server.services import owner_service
from server.models import Owner

class Command(BaseCommand):
    help = '''
    This command will invite the owner with the given phone number to come
    and set their password in the app. Creates an auth.User if one doesn't exist.
    args:
    - phone_number(s): the phone number(s) of the owner to send an invite to.
    '''

    def add_arguments(self, parser):
        parser.add_argument('phone_numbers', nargs='+', type=str)

    def handle(self, *args, **options):
        phone_numbers = options['phone_numbers']
        for phone_number in phone_numbers:
            try:
                created, auth_user = owner_service.invite_legacy_owner(phone_number)
                if created:
                    self.stdout.write('Auth user created, and invite sent for {}.\n'.format(phone_number))
                else:
                    self.stdout.write('Owner {} was already signed up. Invite sent anyway.\n'.format(phone_number))
            except Owner.DoesNotExist:
                self.stdout.write('ERROR inviting {}. Owner or UserAccount didn\'t exist.\n'.format(phone_number))
